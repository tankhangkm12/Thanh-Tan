"""Contracts between agentflow parts, and between agentflow and plugin families.

A plugin family talks to agentflow only through a workflow file that a
``WorkflowSource`` loads; agentflow never imports family code.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol, runtime_checkable

from agentflow.models import CommandResult, ProbeResult, ScanResult, State, Workflow


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

    def commit(self, message: str) -> str:
        """Commit what is staged; return the new commit's sha."""
        ...


@runtime_checkable
class SecretScanner(Protocol):
    """Scans staged changes for secrets. Raises ``AgentflowError`` when the scan cannot run."""

    def scan_staged(self, repo: Path) -> ScanResult: ...


@runtime_checkable
class BranchLookup(Protocol):
    """Read-only branch facts the guard needs about a directory's repository."""

    def current_branch(self, directory: Path) -> str | None:
        """Checked-out branch, or ``None`` when detached, unknown or not a repository."""
        ...

    def branch_exists(self, directory: Path, name: str) -> bool: ...
