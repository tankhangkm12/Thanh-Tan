"""Fixed values used across agentflow: file names, enums, exit codes and keys.

No other module should spell these values as string literals.
"""

from enum import IntEnum, StrEnum

PACKAGE_NAME = "agentflow"
SCHEMA_VERSION = 1
ENCODING = "utf-8"

# Workspace layout (relative to the project root).
WORKSPACE_DIR = ".agentflow"
STATE_FILE = "state.json"
STATE_MD_FILE = "STATE.md"
CONFIG_FILE = "config.yaml"
WORKFLOW_COPY_FILE = "workflow.yaml"
DECISIONS_DIR = "decisions"
TASKS_DIR = "tasks"
WORKSPACE_SUBDIRS = (DECISIONS_DIR, TASKS_DIR, "project", "knowledge")
# Per-task files: <workspace>/tasks/<task id>/reports/<step id>.md
REPORTS_DIR = "reports"
MARKDOWN_SUFFIX = ".md"
GITKEEP_FILE = ".gitkeep"
EXCLUDE_ENTRY = f"{WORKSPACE_DIR}/"
TMP_SUFFIX = ".tmp"

# Schemas shipped inside the package.
SCHEMAS_DIR = "schemas"
WORKFLOW_SCHEMA_FILE = "workflow.schema.json"
STATE_SCHEMA_FILE = "state.schema.json"
CONFIG_SCHEMA_FILE = "config.schema.json"

# Git plumbing.
GIT_EXECUTABLE = "git"
GIT_TOPLEVEL_ARGS = ("rev-parse", "--show-toplevel")
GIT_PATH_ARGS = ("rev-parse", "--git-path")
GIT_EXCLUDE_PATH = "info/exclude"

TOOL_TIMEOUT_SECONDS = 15
VERSION_FLAG = "--version"
ENGINE_INFO_ARG = "info"

# Gitflow: where each task type branches from.
MAIN_BRANCH = "main"
DEVELOP_BRANCH = "develop"
PROTECTED_BRANCHES = frozenset({MAIN_BRANCH, DEVELOP_BRANCH})
BRANCH_SEPARATOR = "/"

# Task ids look like T-001; branch slugs come from the task title.
TASK_ID_PREFIX = "T-"
TASK_ID_DIGITS = 3
SLUG_MAX_LENGTH = 40
SLUG_FALLBACK = "task"
COMMIT_PREFIX_SEPARATOR = ": "

# Secret scanning with Gitleaks in a container. The image is pinned on purpose.
GITLEAKS_IMAGE = "zricethezav/gitleaks:v8.24.0"
SCAN_TIMEOUT_SECONDS = 900
# Exit code Gitleaks is told to use for "leaks found", so it differs from its own errors.
GITLEAKS_LEAKS_EXIT_CODE = 99
CONTAINER_REPO_DIR = "/repo"


class ExitCode(IntEnum):
    OK = 0
    ERROR = 1
    USAGE = 2
    MISSING_REQUIREMENT = 3
    NOT_GIT_REPO = 4
    NO_WORKSPACE = 5
    INVALID_WORKFLOW = 6
    INVALID_STATE = 7
    WORKFLOW_MISMATCH = 8
    WORKFLOW_NOT_FOUND = 9
    SYNC_BLOCKED = 10
    INVALID_CONFIG = 11
    TASK_CONFLICT = 12
    NO_ACTIVE_TASK = 13
    INVALID_TRANSITION = 14
    DIRTY_WORKING_TREE = 15
    BRANCH_PROBLEM = 16
    NOTHING_STAGED = 17
    SECRETS_FOUND = 18
    ENGINE_NOT_RUNNING = 19
    SCAN_FAILED = 20
    GIT_FAILED = 21
    INVALID_INPUT = 22
    UNKNOWN_STEP = 23


class TaskType(StrEnum):
    FEATURE = "feature"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"


TASK_BASE_BRANCH = {
    TaskType.FEATURE: DEVELOP_BRANCH,
    TaskType.BUGFIX: DEVELOP_BRANCH,
    TaskType.HOTFIX: MAIN_BRANCH,
}


class TaskEvent(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    APPROVE = "approve"
    CANCEL = "cancel"


# What `task advance --result` accepts.
STEP_RESULTS = (TaskEvent.PASS, TaskEvent.FAIL)


class TaskStatus(StrEnum):
    OPEN = "open"
    BLOCKED = "blocked"
    DONE = "done"
    CANCELLED = "cancelled"


# Task statuses that mean the task is still somewhere inside the workflow.
IN_FLIGHT_TASK_STATUSES = frozenset({TaskStatus.OPEN, TaskStatus.BLOCKED})


class StepStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    AWAITING_APPROVAL = "awaiting_approval"
    PASSED = "passed"
    FAILED = "failed"


class HistoryEvent(StrEnum):
    STARTED = "started"
    PASSED = "passed"
    FAILED = "failed"
    APPROVED = "approved"
    BLOCKED = "blocked"
    # A person approved a blocked task, overriding the block.
    RESUMED = "resumed"
    CANCELLED = "cancelled"
    DONE = "done"


class ActionKind(StrEnum):
    START_TASK = "start_task"
    CONTINUE = "continue"
    AWAIT_APPROVAL = "await_approval"
    ADVANCE = "advance"
    LOOP = "loop"
    BLOCKED = "blocked"
    DONE = "done"


class DriftStatus(StrEnum):
    IN_SYNC = "in_sync"
    SOURCE_CHANGED = "source_changed"
    SOURCE_MISSING = "source_missing"


class SyncOutcome(StrEnum):
    UNCHANGED = "unchanged"
    UPDATED = "updated"


class Tool(StrEnum):
    UV = "uv"
    GIT = "git"
    DOCKER = "docker"
    PODMAN = "podman"


class ToolStatus(StrEnum):
    OK = "ok"
    MISSING = "missing"
    WARNING = "warning"


REQUIRED_TOOLS = (Tool.UV, Tool.GIT)
# At least one of these must be installed.
CONTAINER_TOOLS = (Tool.DOCKER, Tool.PODMAN)

INSTALL_URLS = {
    Tool.UV: "https://docs.astral.sh/uv/getting-started/installation/",
    Tool.GIT: "https://git-scm.com/downloads",
    Tool.DOCKER: "https://docs.docker.com/get-started/get-docker/",
    Tool.PODMAN: "https://podman.io/docs/installation",
}


class Command(StrEnum):
    DOCTOR = "doctor"
    INIT = "init"
    STATUS = "status"
    NEXT = "next"
    WORKFLOW = "workflow"
    TASK = "task"
    REPORT = "report"
    COMMIT = "commit"
    GUARD = "guard"


class WorkflowCommand(StrEnum):
    SYNC = "sync"


class TaskCommand(StrEnum):
    NEW = "new"
    ADVANCE = "advance"
    APPROVE = "approve"
    CANCEL = "cancel"


class GuardDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class GuardRule(StrEnum):
    """Why `agentflow guard` denied a shell command."""

    PUSH = "push"
    PROTECTED_BRANCH = "protected-branch"
    RESET_HARD = "reset-hard"
    CLEAN_FORCE_DIRS = "clean-force-dirs"
    BRANCH_FORCE_DELETE = "branch-force-delete"
    TAG_DELETE = "tag-delete"


class GuardKey(StrEnum):
    """Keys of the JSON that `agentflow guard` reads and writes."""

    COMMAND = "command"
    CWD = "cwd"
    DECISION = "decision"
    REASON = "reason"
    RULE = "rule"


class WorkflowKey(StrEnum):
    SCHEMA_VERSION = "schema_version"
    FAMILY = "family"
    MAX_ROUNDS = "max_rounds"
    STEPS = "steps"
    ID = "id"
    NAME = "name"
    ROLE = "role"
    REQUIRES_APPROVAL = "requires_approval"
    ON_FAIL = "on_fail"


class StateKey(StrEnum):
    SCHEMA_VERSION = "schema_version"
    UPDATED_AT = "updated_at"
    ACTIVE_TASK_ID = "active_task_id"
    TASKS = "tasks"
    ID = "id"
    TITLE = "title"
    STATUS = "status"
    CURRENT_STEP = "current_step"
    STEP_STATUS = "step_status"
    LOOP_ROUND = "loop_round"
    BRANCH = "branch"
    HISTORY = "history"
    AT = "at"
    STEP = "step"
    EVENT = "event"


class ConfigKey(StrEnum):
    SCHEMA_VERSION = "schema_version"
    WORKFLOW = "workflow"
    FAMILY = "family"
    SOURCE_PATH = "source_path"
    SHA256 = "sha256"
