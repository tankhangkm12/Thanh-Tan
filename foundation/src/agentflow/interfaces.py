"""Contracts between agentflow parts, and between agentflow and plugin families.

A plugin family talks to agentflow only through a workflow file that a
``WorkflowSource`` loads; agentflow never imports family code.
"""

from collections.abc import Collection, Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from typing import TYPE_CHECKING

from agentflow.constants import HookEvent, ProjectSection
from agentflow.models import (
    CommandResult,
    CommitInfo,
    ConventionInfo,
    HookInput,
    HookReply,
    KnowledgeFile,
    KnowledgeHit,
    NextInfo,
    PlanCheckInfo,
    ProbeResult,
    ProjectWriteInfo,
    ReportInfo,
    ScanResult,
    ScanSummaryInfo,
    State,
    StatusInfo,
    Workflow,
)


if TYPE_CHECKING:
    from agentflow.workspace import WorkspacePaths


@runtime_checkable
class WorkflowSource(Protocol):
    """Supplies a family's validated workflow and a fingerprint of its raw content."""

    def load(self) -> Workflow: ...

    def fingerprint(self) -> str:
        """sha256 hex digest of the raw workflow bytes."""
        ...


@runtime_checkable
class StateStore(Protocol):
    """Reads and writes the workspace state; ``save`` also regenerates STATE.md."""

    def load(self) -> State: ...

    def save(self, state: State) -> State:
        """Persist ``state`` and return it as written (with ``updated_at`` stamped)."""
        ...


@runtime_checkable
class ToolProbe(Protocol):
    """Looks up and runs external tools, so doctor can be tested without them."""

    def which(self, name: str) -> str | None: ...

    def run(self, args: Sequence[str]) -> ProbeResult: ...


@runtime_checkable
class CommandRunner(Protocol):
    """Runs external programs and captures their output, so callers can be tested with a fake."""

    def which(self, name: str) -> str | None: ...

    def run(self, args: Sequence[str], cwd: Path | None, timeout: int) -> CommandResult:
        """Run ``args``; a program that cannot start or times out reports a non-zero ``returncode``."""
        ...


@runtime_checkable
class GitClient(Protocol):
    """The git operations the task lifecycle needs, for one repository."""

    root: Path

    def current_branch(self) -> str | None:
        """Checked-out branch name, or ``None`` on a detached HEAD."""
        ...

    def is_clean(self) -> bool:
        """No staged, unstaged or untracked changes (ignored files do not count)."""
        ...

    def branch_exists(self, name: str) -> bool: ...

    def create_branch(self, name: str, base: str) -> None:
        """Create ``name`` from ``base`` and switch to it."""
        ...

    def has_staged_changes(self) -> bool: ...

    def staged_files(self) -> Sequence[str]:
        """Paths with staged changes (additions, modifications, renames and deletions)."""
        ...

    def commit(self, message: str) -> str:
        """Commit what is staged; return the new commit's sha."""
        ...

    def rev_parse(self, ref: str) -> str:
        """Full sha ``ref`` points to; raises when it does not exist."""
        ...

    def tag_exists(self, name: str) -> bool: ...

    def create_tag(self, name: str, target: str, message: str) -> None:
        """Create an annotated tag on ``target``."""
        ...

    def commits_between(self, base: str, head: str) -> Sequence[CommitInfo]:
        """Commits reachable from ``head`` and not from ``base``, oldest first."""
        ...

    def changed_files(self, base: str, head: str) -> Sequence[str]:
        """Paths added, copied, modified or renamed from the merge base of ``base`` and ``head`` to ``head``."""
        ...

    def identity(self) -> str:
        """The configured committer as ``Name <email>``."""
        ...


@runtime_checkable
class SecretScanner(Protocol):
    """Scans staged changes for secrets. Raises ``AgentflowError`` when the scan cannot run."""

    def scan_staged(self, repo: Path) -> ScanResult: ...


@runtime_checkable
class HookAdapter(Protocol):
    """Translates between one CLI's hook payloads and agentflow's CLI-neutral hook model."""

    def read(self, event: HookEvent, payload: Mapping[str, Any]) -> HookInput: ...

    def render(self, event: HookEvent, reply: HookReply) -> str:
        """The text to print on stdout for ``reply``; empty when the CLI wants no output."""
        ...


@runtime_checkable
class BranchLookup(Protocol):
    """Read-only branch facts the guard needs about a directory's repository."""

    def current_branch(self, directory: Path) -> str | None:
        """Checked-out branch, or ``None`` when detached, unknown or not a repository."""
        ...

    def branch_exists(self, directory: Path, name: str) -> bool: ...


@runtime_checkable
class RoleRegistry(Protocol):
    """The roles a plan item may be given: the workflow's own plus those extensions register."""

    def roles(self) -> Collection[str]: ...


@runtime_checkable
class PlanRule(Protocol):
    """An extra check on one plan item (supplied by an extension); returns problem messages."""

    def problems(self, item: Any) -> Sequence[str]: ...


@runtime_checkable
class PlanWideRule(Protocol):
    """A check on a whole plan (such as the order of its items); returns ``(item code or None, message)`` pairs."""

    def problems(self, items: Sequence[Any]) -> Sequence[tuple[str | None, str]]: ...


@runtime_checkable
class GateRunner(Protocol):
    """Checks a step's gates; each returned string is a reason the step may not pass yet."""

    def problems(self, task: Any, step: Any) -> Sequence[str]: ...


@runtime_checkable
class ProjectLocator(Protocol):
    """Finds the project's workspace for a process that may not be running inside the project."""

    def find(self) -> "WorkspacePaths":
        """The workspace, or ``AgentflowError`` (``NO_WORKSPACE``) saying where it looked."""
        ...


@runtime_checkable
class WorkspaceService(Protocol):
    """What an agent may do with a workspace, whether it asks through the CLI or through MCP tools.

    Every call reads the workspace afresh (a server outlives many task changes) and raises ``AgentflowError``
    when a rule is broken. Nothing here approves, cancels, seals, decides, registers extensions or changes
    settings: those stay with a person.
    """

    def status(self) -> StatusInfo: ...

    def next_step(self) -> NextInfo: ...

    def plan_check(self) -> PlanCheckInfo: ...

    def write_report(self, step: str, content: str) -> ReportInfo: ...

    def write_project(self, section: ProjectSection, content: str) -> ProjectWriteInfo: ...

    def scan_summary(self) -> ScanSummaryInfo: ...

    def conventions(self) -> Sequence[ConventionInfo]: ...

    def knowledge_search(self, query: str, limit: int) -> Sequence[KnowledgeHit]: ...

    def knowledge_read(self, file: str) -> KnowledgeFile: ...


@runtime_checkable
class WriteTargetPolicy(Protocol):
    """Decides whether a path may be written by an agent's tools or shell commands."""

    def is_protected(self, target: Path | str, cwd: Path) -> bool:
        """True when ``target`` (absolute, or relative to ``cwd``) lies inside an agentflow workspace."""
        ...


@runtime_checkable
class WorkspaceLookup(Protocol):
    """Whether the repository around a directory has an agentflow workspace."""

    def has_workspace(self, directory: Path) -> bool: ...
