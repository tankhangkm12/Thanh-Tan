"""The project documents under ``.agentflow/project/`` and what a person does to them (confirming conventions)."""

from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

from agentflow.constants import (
    ENCODING,
    MARKDOWN_SUFFIX,
    PROJECT_DIR,
    ConventionPrefix,
    ConventionStatus,
    ExitCode,
    ProjectSection,
)
from agentflow.conventions import ConventionDoc, parse_conventions, render_conventions, validate_conventions
from agentflow.errors import AgentflowError
from agentflow.fsutil import write_text_atomic


def conventions_path(workspace_dir: Path) -> Path:
    return workspace_dir / PROJECT_DIR / f"{ProjectSection.CONVENTIONS}{MARKDOWN_SUFFIX}"


def load_conventions(workspace_dir: Path) -> ConventionDoc | None:
    """The project's conventions, or ``None`` when no scout has written them yet."""
    path = conventions_path(workspace_dir)
    if not path.is_file():
        return None
    return parse_conventions(path.read_text(encoding=ENCODING), ConventionPrefix.PROJECT)


@dataclass(frozen=True)
class ConfirmResult:
    confirmed: tuple[str, ...]
    already: tuple[str, ...]
    unconfirmed: tuple[str, ...]
    open_questions: tuple[str, ...]


def confirm_conventions(workspace_dir: Path, codes: Sequence[str], everything: bool) -> ConfirmResult:
    """For a person: mark conventions as confirmed (all of them, or the named ones) and rewrite the file."""
    if bool(codes) == everything:
        raise AgentflowError("name the conventions to confirm (PC-01 PC-02 ...) or use --all, not both", ExitCode.INVALID_INPUT)
    doc = load_conventions(workspace_dir)
    if doc is None or not doc.conventions:
        raise AgentflowError("there are no project conventions yet: run the setup skill first", ExitCode.INVALID_INPUT)
    problems = validate_conventions(doc)
    if problems:
        raise AgentflowError(
            "conventions.md has problems, fix them first:\n- " + "\n- ".join(problems), ExitCode.CONVENTIONS_INVALID
        )
    known = {item.code for item in doc.conventions}
    missing = [code for code in codes if code not in known]
    if missing:
        raise AgentflowError(f"no such convention: {', '.join(missing)} (have: {', '.join(sorted(known))})", ExitCode.INVALID_INPUT)
    wanted = known if everything else set(codes)
    confirmed: list[str] = []
    already: list[str] = []
    updated = []
    for item in doc.conventions:
        if item.code in wanted and item.status is ConventionStatus.CONFIRMED:
            already.append(item.code)
        elif item.code in wanted:
            confirmed.append(item.code)
            item = replace(item, status=ConventionStatus.CONFIRMED)
        updated.append(item)
    if confirmed:
        write_text_atomic(conventions_path(workspace_dir), render_conventions(replace(doc, conventions=tuple(updated))))
    left = tuple(item.code for item in updated if item.status is ConventionStatus.UNCONFIRMED)
    return ConfirmResult(tuple(confirmed), tuple(already), left, tuple(q.code for q in doc.questions))


def unconfirmed_conventions(workspace_dir: Path) -> tuple[str, ...]:
    """Codes of the project conventions no person has confirmed yet (none when there is no file)."""
    doc = load_conventions(workspace_dir)
    if doc is None:
        return ()
    return tuple(item.code for item in doc.conventions if item.status is ConventionStatus.UNCONFIRMED)
