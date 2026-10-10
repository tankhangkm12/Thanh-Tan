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
# Git trailer that ties a commit to a plan item.
PLAN_ITEM_TRAILER = "Plan-Item"
SUMMARY_FILE = "summary.md"

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
    PLAN_INVALID = 24
    GATE_FAILED = 25
    TASK_NOT_SEALED = 26
    SCAN_BLOCKED = 27
    EXTENSION_INVALID = 28
    SETTINGS_INVALID = 29


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
    BLOCKED = "blocked"


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
    HOOK = "hook"
    PLAN = "plan"


class WorkflowCommand(StrEnum):
    SYNC = "sync"


class TaskCommand(StrEnum):
    NEW = "new"
    ADVANCE = "advance"
    APPROVE = "approve"
    CANCEL = "cancel"
    SEAL = "seal"


class HookEvent(StrEnum):
    """What a hook is for; each CLI maps its own event names onto these."""

    SESSION_START = "session-start"
    PRE_TOOL = "pre-tool"
    STOP = "stop"


class CliKind(StrEnum):
    CLAUDE = "claude"
    ANTIGRAVITY = "antigravity"


class ReplyKind(StrEnum):
    """What the hook logic wants to tell the CLI; adapters turn it into each CLI's format."""

    NONE = "none"
    DENY = "deny"
    CONTEXT = "context"
    REMINDER = "reminder"


class ClaudeHookKey(StrEnum):
    CWD = "cwd"
    TOOL_INPUT = "tool_input"
    COMMAND = "command"
    STOP_HOOK_ACTIVE = "stop_hook_active"
    HOOK_SPECIFIC_OUTPUT = "hookSpecificOutput"
    HOOK_EVENT_NAME = "hookEventName"
    PERMISSION_DECISION = "permissionDecision"
    PERMISSION_DECISION_REASON = "permissionDecisionReason"
    ADDITIONAL_CONTEXT = "additionalContext"
    SYSTEM_MESSAGE = "systemMessage"


class ClaudeHookValue(StrEnum):
    PRE_TOOL_USE = "PreToolUse"
    SESSION_START = "SessionStart"
    DENY = "deny"


class AntigravityHookKey(StrEnum):
    WORKSPACE_PATHS = "workspacePaths"
    TOOL_CALL = "toolCall"
    ARGS = "args"
    COMMAND_LINE = "CommandLine"
    CWD = "Cwd"
    INVOCATION_NUM = "invocationNum"
    INJECT_STEPS = "injectSteps"
    EPHEMERAL_MESSAGE = "ephemeralMessage"
    DECISION = "decision"
    REASON = "reason"


class AntigravityDecision(StrEnum):
    DENY = "deny"
    # Any value but "continue" lets the agent stop.
    ALLOW_STOP = "allow"


# Antigravity numbers model invocations from 0; only the first one gets the session summary.
ANTIGRAVITY_FIRST_INVOCATION = 0
# What a Antigravity PreToolUse hook prints when it has no objection. An empty string means "no output";
# its handling by `agy` is checked by the install smoke test (see tools/).
ANTIGRAVITY_PRE_TOOL_PASS_OUTPUT = ""
EMPTY_JSON_OBJECT = "{}"


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
    DIRECT_COMMIT = "direct-commit"
    APPROVAL_TAG = "approval-tag"
    PERSON_ONLY = "person-only"


class GuardKey(StrEnum):
    """Keys of the JSON that `agentflow guard` reads and writes."""

    COMMAND = "command"
    CWD = "cwd"
    DECISION = "decision"
    REASON = "reason"
    RULE = "rule"


# Tags `agentflow task approve` creates; nobody else may create refs under this prefix.
APPROVAL_TAG_PREFIX = "agentflow/"
APPROVAL_TAG_SUFFIX = "approved"
TAG_REF_PREFIX = "refs/tags/"
AGENTFLOW_PROGRAM = "agentflow"


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
    GATES = "gates"


class GateKind(StrEnum):
    """Checks a step must pass before ``task advance --result pass`` is accepted."""

    PLAN_VALID = "plan-valid"
    SCANS_CLEAN = "scans-clean"


class PlanCommand(StrEnum):
    CHECK = "check"


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


# ----------------------------------------------------------------- plan

class PlanField(StrEnum):
    """Field names of a plan item (a bullet under its ``### C<n>`` heading)."""

    ROLE = "role"
    FILES = "files"
    DONE_WHEN = "done-when"
    DOCS = "docs"


PLAN_ITEM_CODE_PATTERN = r"C[0-9]+"
PLAN_NO_DOCS_PREFIX = "không có"
PLAN_NO_FILES_PREFIX = "không có"
