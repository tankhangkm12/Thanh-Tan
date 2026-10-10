"""What an agent may do with a workspace: the one implementation behind both the CLI and the MCP tools."""

import re
from collections.abc import Sequence
from dataclasses import replace
from pathlib import Path

from agentflow.constants import (
    ENCODING,
    IN_FLIGHT_TASK_STATUSES,
    KNOWLEDGE_DIR,
    KNOWLEDGE_HIT_MAX_CHARS,
    KNOWLEDGE_MAX_FILE_BYTES,
    KNOWLEDGE_SEARCH_MAX_LIMIT,
    KNOWLEDGE_TEXT_SUFFIXES,
    MARKDOWN_SUFFIX,
    PROJECT_DIR,
    ConventionPrefix,
    ConventionStatus,
    ExitCode,
    GateKind,
    ProjectSection,
)
from agentflow.conventions import Convention, ConventionDoc, parse_conventions, render_conventions, validate_conventions
from agentflow.engine import next_action
from agentflow.errors import AgentflowError
from agentflow.fsutil import write_text_atomic
from agentflow.gates import plan_problems, plan_report_path
from agentflow.convention_sources import answered_questions, load_effective_conventions
from agentflow.models import (
    ConventionInfo,
    KnowledgeFile,
    KnowledgeHit,
    NextInfo,
    PlanCheckInfo,
    ProjectWriteInfo,
    ReportInfo,
    ScanSummaryInfo,
    ScanToolInfo,
    State,
    StatusInfo,
    Task,
    TaskInfo,
    Workflow,
)
from agentflow.projectcontext import load_project_context
from agentflow.render import describe_action
from agentflow.scan import unsuppressed_blocking
from agentflow.scan_store import ScanStore, suppressed_ids
from agentflow.state import JsonStateStore
from agentflow.tasks import require_active_task, write_report
from agentflow.workspace import WorkspacePaths, load_workspace_workflow

_CRLF = "\r\n"
_LF = "\n"
_DRIVE = re.compile(r"^[A-Za-z]:")
_SEPARATORS = re.compile(r"[\\/]+")


class WorkspaceServices:
    """``WorkspaceService`` for a real workspace. Each call reads the workspace afresh."""

    def __init__(self, paths: WorkspacePaths) -> None:
        self.paths = paths

    def _open(self) -> tuple[Workflow, State]:
        workflow = load_workspace_workflow(self.paths)
        return workflow, JsonStateStore(self.paths.dir, workflow).load()

    # ----------------------------------------------------------- task state

    def status(self) -> StatusInfo:
        workflow, state = self._open()
        task = state.active_task()
        info = None
        if task is not None:
            info = TaskInfo(
                task.id, task.title, task.branch, str(task.status), task.current_step, str(task.step_status),
                task.loop_round, workflow.max_rounds, task.size,
            )  # fmt: skip
        return StatusInfo(str(self.paths.dir), workflow.family, info, describe_action(next_action(workflow, task)))

    def next_step(self) -> NextInfo:
        workflow, state = self._open()
        action = next_action(workflow, state.active_task())
        return NextInfo(str(action.kind), describe_action(action))

    # ------------------------------------------------------- plan and reports

    def plan_check(self) -> PlanCheckInfo:
        workflow, state = self._open()
        task = require_active_task(state)
        step = next((s for s in workflow.steps if GateKind.PLAN_VALID in s.gates), None)
        if step is None:
            raise AgentflowError("the workflow has no step that checks a plan", ExitCode.INVALID_INPUT)
        path = plan_report_path(self.paths.dir, task.id, step.id)
        if not path.is_file():
            raise AgentflowError(f"no plan report yet: {path}", ExitCode.PLAN_INVALID)
        project = load_project_context(self.paths.dir, workflow, task)
        problems = plan_problems(path.read_text(encoding=ENCODING), project, answered_questions(self.paths.dir, task.id))
        return PlanCheckInfo(not problems, tuple(problems))

    def write_report(self, step: str, content: str) -> ReportInfo:
        workflow, state = self._open()
        path = write_report(self.paths.dir, workflow, require_active_task(state), step, content)
        return ReportInfo(str(path), path.stat().st_size)

    # ------------------------------------------------------ project documents

    def write_project(self, section: ProjectSection, content: str) -> ProjectWriteInfo:
        """Store a project document. Documents change between tasks (during setup), not while a task is running."""
        if not content.strip():
            raise AgentflowError("the document is empty", ExitCode.INVALID_INPUT)
        _, state = self._open()
        running = [t.id for t in state.tasks if t.status in IN_FLIGHT_TASK_STATUSES]
        if running:
            raise AgentflowError(
                f"task {', '.join(running)} is still open: project documents are written between tasks, not during one",
                ExitCode.PROJECT_WRITE_REFUSED,
            )
        text = content.replace(_CRLF, _LF)
        path = self.paths.dir / PROJECT_DIR / f"{section}{MARKDOWN_SUFFIX}"
        path.parent.mkdir(parents=True, exist_ok=True)
        if section is not ProjectSection.CONVENTIONS:
            write_text_atomic(path, text if text.endswith(_LF) else text + _LF)
            return ProjectWriteInfo(str(path), path.stat().st_size)
        document, demoted = _agent_conventions(text, path)
        write_text_atomic(path, render_conventions(document))
        return ProjectWriteInfo(str(path), path.stat().st_size, len(document.conventions), len(document.questions), demoted)

    # ------------------------------------------------------------------ scans

    def scan_summary(self) -> ScanSummaryInfo:
        _, state = self._open()
        task = state.active_task()
        if task is None:
            return ScanSummaryInfo(None)
        return _scan_summary(self.paths.dir, task)

    # --------------------------------------------------------------- knowledge

    def conventions(self) -> Sequence[ConventionInfo]:
        effective = load_effective_conventions(self.paths.dir)
        enforced = {id(item) for item in effective.enforced}
        return [
            ConventionInfo(
                item.convention.code, item.convention.title, str(item.source), str(item.convention.check),
                item.convention.rule, item.convention.description or "", id(item) in enforced,
            )
            for item in effective.items
        ]  # fmt: skip

    def knowledge_search(self, query: str, limit: int) -> Sequence[KnowledgeHit]:
        needle = query.strip().lower()
        if not needle:
            raise AgentflowError("the search text is empty", ExitCode.INVALID_INPUT)
        limit = max(1, min(limit, KNOWLEDGE_SEARCH_MAX_LIMIT))
        root = self._knowledge_root()
        hits: list[KnowledgeHit] = []
        for path in sorted(root.rglob("*")) if root.is_dir() else ():
            if not _readable(path):
                continue
            relative = path.relative_to(root).as_posix()
            for number, line in enumerate(path.read_text(encoding=ENCODING, errors="replace").splitlines(), start=1):
                if needle in line.lower():
                    hits.append(KnowledgeHit(relative, number, line.strip()[:KNOWLEDGE_HIT_MAX_CHARS]))
                    if len(hits) >= limit:
                        return hits
        return hits

    def knowledge_read(self, file: str) -> KnowledgeFile:
        root = self._knowledge_root().resolve()
        name = file.strip()
        parts = [part for part in _SEPARATORS.split(name) if part]
        if not parts or name.startswith(("/", "\\")) or _DRIVE.match(name) or ".." in parts:
            raise AgentflowError(f"'{file}' is not a path inside {KNOWLEDGE_DIR}/", ExitCode.INVALID_INPUT)
        target = (root.joinpath(*parts)).resolve()
        if root != target and root not in target.parents:
            raise AgentflowError(f"'{file}' is not a path inside {KNOWLEDGE_DIR}/", ExitCode.INVALID_INPUT)
        if not target.is_file():
            raise AgentflowError(f"no file '{file}' in {KNOWLEDGE_DIR}/", ExitCode.KNOWLEDGE_NOT_FOUND)
        if not _readable(target):
            raise AgentflowError(f"'{file}' is not a text file of readable size", ExitCode.INVALID_INPUT)
        return KnowledgeFile("/".join(parts), target.read_text(encoding=ENCODING, errors="replace"))

    def _knowledge_root(self) -> Path:
        return self.paths.dir / KNOWLEDGE_DIR


def _agent_conventions(text: str, path: Path) -> tuple[ConventionDoc, tuple[str, ...]]:
    """The conventions an agent wrote, with the statuses only a person may set put right.

    A convention keeps ``confirmed`` only when it is unchanged from what a person confirmed; a changed one goes back
    to ``unconfirmed``, and a new one is never confirmed. A confirmed convention cannot be left out.
    """
    written = parse_conventions(text, ConventionPrefix.PROJECT)
    problems = validate_conventions(written)
    if problems:
        raise AgentflowError("the conventions are not valid:\n- " + "\n- ".join(problems), ExitCode.CONVENTIONS_INVALID)
    before = {c.code: c for c in parse_conventions(path.read_text(encoding=ENCODING), ConventionPrefix.PROJECT).conventions} if path.is_file() else {}
    confirmed = {code: c for code, c in before.items() if c.status is ConventionStatus.CONFIRMED}
    dropped = sorted(set(confirmed) - {c.code for c in written.conventions})
    if dropped:
        raise AgentflowError(
            f"{', '.join(dropped)} is confirmed: only a person removes a confirmed convention (by editing the file)",
            ExitCode.PROJECT_WRITE_REFUSED,
        )
    kept: list[Convention] = []
    demoted: list[str] = []
    for item in written.conventions:
        prior = confirmed.get(item.code)
        unchanged = prior is not None and prior.same_content(item)
        status = ConventionStatus.CONFIRMED if unchanged else ConventionStatus.UNCONFIRMED
        if status is not ConventionStatus.CONFIRMED and (prior is not None or item.status is ConventionStatus.CONFIRMED):
            demoted.append(item.code)
        kept.append(replace(item, status=status))
    return replace(written, conventions=tuple(kept)), tuple(demoted)


def _readable(path: Path) -> bool:
    return path.is_file() and path.suffix.lower() in KNOWLEDGE_TEXT_SUFFIXES and path.stat().st_size <= KNOWLEDGE_MAX_FILE_BYTES


def _scan_summary(workspace_dir: Path, task: Task) -> ScanSummaryInfo:
    suppressed = suppressed_ids(workspace_dir, task.id)
    tools: list[ScanToolInfo] = []
    blocking: list[str] = []
    for outcome in ScanStore(workspace_dir).load(task.id).values():
        left = unsuppressed_blocking(outcome, suppressed)
        tools.append(ScanToolInfo(outcome.tool, str(outcome.status), len(outcome.findings), len(left)))
        blocking += [finding.id for finding in left]
    return ScanSummaryInfo(task.id, tuple(tools), tuple(blocking))
