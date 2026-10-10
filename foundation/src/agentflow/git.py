"""Git through its command line: the ``GitClient`` for one repository and the guard's ``BranchLookup``."""

import subprocess
from pathlib import Path

from agentflow.constants import ENCODING, GIT_EXECUTABLE, ExitCode
from agentflow.errors import AgentflowError

CURRENT_BRANCH_ARGS = ("symbolic-ref", "--quiet", "--short", "HEAD")
STATUS_ARGS = ("status", "--porcelain")
VERIFY_ARGS = ("rev-parse", "--verify", "--quiet")
HEAD_SHA_ARGS = ("rev-parse", "HEAD")
SWITCH_CREATE_ARGS = ("switch", "--quiet", "--create")
STAGED_QUIET_ARGS = ("diff", "--cached", "--quiet")
COMMIT_ARGS = ("commit", "--quiet", "--message")
HEADS_REF_PREFIX = "refs/heads/"
# `git diff --quiet` exits 1 when there are differences.
DIFF_HAS_CHANGES = 1


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            [GIT_EXECUTABLE, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding=ENCODING,
            errors="replace",
            check=False,
        )
    except FileNotFoundError as exc:
        raise AgentflowError("git is not installed or not on PATH", ExitCode.MISSING_REQUIREMENT) from exc


def _checked(cwd: Path, *args: str) -> str:
    result = run_git(cwd, *args)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AgentflowError(f"git {' '.join(args)} failed: {detail}", ExitCode.GIT_FAILED)
    return result.stdout.strip()


class SubprocessGit:
    """``GitClient`` for the repository at ``root``."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def current_branch(self) -> str | None:
        result = run_git(self.root, *CURRENT_BRANCH_ARGS)
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def is_clean(self) -> bool:
        return _checked(self.root, *STATUS_ARGS) == ""

    def branch_exists(self, name: str) -> bool:
        return run_git(self.root, *VERIFY_ARGS, HEADS_REF_PREFIX + name).returncode == 0

    def create_branch(self, name: str, base: str) -> None:
        _checked(self.root, *SWITCH_CREATE_ARGS, name, base)

    def has_staged_changes(self) -> bool:
        result = run_git(self.root, *STAGED_QUIET_ARGS)
        if result.returncode not in (0, DIFF_HAS_CHANGES):
            raise AgentflowError(f"cannot read staged changes: {result.stderr.strip()}", ExitCode.GIT_FAILED)
        return result.returncode == DIFF_HAS_CHANGES

    def commit(self, message: str) -> str:
        _checked(self.root, *COMMIT_ARGS, message)
        return _checked(self.root, *HEAD_SHA_ARGS)


class GitBranchLookup:
    """``BranchLookup`` that asks git; any failure (no repository, missing directory) reads as unknown."""

    def current_branch(self, directory: Path) -> str | None:
        if not directory.is_dir():
            return None
        result = run_git(directory, *CURRENT_BRANCH_ARGS)
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def branch_exists(self, directory: Path, name: str) -> bool:
        if not directory.is_dir():
            return False
        return run_git(directory, *VERIFY_ARGS, HEADS_REF_PREFIX + name).returncode == 0
