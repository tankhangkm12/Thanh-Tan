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
WORKSPACE_SUBDIRS = ("decisions", "tasks", "project", "knowledge")
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
    LOOPED = "looped"


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


class WorkflowCommand(StrEnum):
    SYNC = "sync"


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
