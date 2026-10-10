"""`agentflow commit`: commit staged changes on the task's own branch, after a clean secret scan."""

from agentflow.constants import COMMIT_PREFIX_SEPARATOR, ExitCode
from agentflow.errors import AgentflowError
from agentflow.interfaces import GitClient, SecretScanner, StateStore
from agentflow.models import CommitResult
from agentflow.tasks import require_active_task

LEAKS_HINT = "secrets were found in the staged changes; nothing was committed. Remove them, restage and retry"


def commit_staged(store: StateStore, git: GitClient, scanner: SecretScanner, message: str) -> CommitResult:
    message = message.strip()
    if not message:
        raise AgentflowError("the commit message is empty", ExitCode.INVALID_INPUT)
    task = require_active_task(store.load())
    if task.branch is None:
        raise AgentflowError(f"task {task.id} has no branch recorded", ExitCode.BRANCH_PROBLEM)
    current = git.current_branch()
    if current != task.branch:
        raise AgentflowError(
            f"task {task.id} lives on branch '{task.branch}' but the checked-out branch is "
            f"'{current or 'none (detached HEAD)'}'; switch to the task branch first",
            ExitCode.BRANCH_PROBLEM,
        )
    if not git.has_staged_changes():
        raise AgentflowError("nothing is staged; `git add` the files to commit first", ExitCode.NOTHING_STAGED)

    scan = scanner.scan_staged(git.root)
    if not scan.clean:
        raise AgentflowError(f"{LEAKS_HINT}:\n{scan.output}", ExitCode.SECRETS_FOUND)

    full_message = f"{task.id}{COMMIT_PREFIX_SEPARATOR}{message}"
    return CommitResult(git.commit(full_message), full_message)
