"""Typed data shared by every agentflow module.

The ``*_from_dict`` helpers expect data that already passed schema validation;
they only map plain JSON/YAML values onto the dataclasses.
"""

from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Any

from agentflow.constants import (
    INSTALL_URLS,
    SCHEMA_VERSION,
    ActionKind,
    ConfigKey,
    HistoryEvent,
    StateKey,
    StepKind,
    StepStatus,
    TaskStatus,
    Tool,
    ToolStatus,
    WorkflowKey,
)

# ---------------------------------------------------------------- workflow


@dataclass(frozen=True)
class LoopSpec:
    back_to: str
    max_rounds: int


@dataclass(frozen=True)
class Step:
    id: str
    name: str
    role: str
    kind: StepKind = StepKind.STEP
    requires_approval: bool = False
    on_fail: str | None = None
    loop: LoopSpec | None = None


@dataclass(frozen=True)
class Workflow:
    schema_version: int
    family: str
    steps: tuple[Step, ...]

    def get_step(self, step_id: str) -> Step | None:
        return next((step for step in self.steps if step.id == step_id), None)

    def main_steps(self) -> tuple[Step, ...]:
        """Steps on the normal path, in order; loop steps are only entered via ``on_fail``."""
        return tuple(step for step in self.steps if step.kind is StepKind.STEP)

    def first_step(self) -> Step:
        return self.main_steps()[0]

    def step_after(self, step_id: str) -> Step | None:
        """The main step that follows ``step_id``, or ``None`` when it is the last one."""
        main = self.main_steps()
        ids = [step.id for step in main]
        position = ids.index(step_id)
        return main[position + 1] if position + 1 < len(main) else None


def workflow_from_dict(data: Mapping[str, Any]) -> Workflow:
    return Workflow(
        schema_version=data[WorkflowKey.SCHEMA_VERSION],
        family=data[WorkflowKey.FAMILY],
        steps=tuple(_step_from_dict(item) for item in data[WorkflowKey.STEPS]),
    )


def _step_from_dict(data: Mapping[str, Any]) -> Step:
    loop = data.get(WorkflowKey.LOOP)
    return Step(
        id=data[WorkflowKey.ID],
        name=data[WorkflowKey.NAME],
        role=data[WorkflowKey.ROLE],
        kind=StepKind(data.get(WorkflowKey.KIND, StepKind.STEP)),
        requires_approval=data.get(WorkflowKey.REQUIRES_APPROVAL, False),
        on_fail=data.get(WorkflowKey.ON_FAIL),
        loop=None
        if loop is None
        else LoopSpec(back_to=loop[WorkflowKey.BACK_TO], max_rounds=loop[WorkflowKey.MAX_ROUNDS]),
    )


# ------------------------------------------------------------------- state


@dataclass(frozen=True)
class HistoryEntry:
    at: str
    step: str
    event: HistoryEvent


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    status: TaskStatus
    current_step: str
    step_status: StepStatus
    loop_round: int = 0
    branch: str | None = None
    history: tuple[HistoryEntry, ...] = ()


@dataclass(frozen=True)
class State:
    schema_version: int = SCHEMA_VERSION
    updated_at: str | None = None
    active_task_id: str | None = None
    tasks: tuple[Task, ...] = ()

    def active_task(self) -> Task | None:
        if self.active_task_id is None:
            return None
        return next((task for task in self.tasks if task.id == self.active_task_id), None)

    def stamped(self, updated_at: str) -> "State":
        return replace(self, updated_at=updated_at)


def state_from_dict(data: Mapping[str, Any]) -> State:
    return State(
        schema_version=data[StateKey.SCHEMA_VERSION],
        updated_at=data[StateKey.UPDATED_AT],
        active_task_id=data[StateKey.ACTIVE_TASK_ID],
        tasks=tuple(_task_from_dict(item) for item in data[StateKey.TASKS]),
    )


def _task_from_dict(data: Mapping[str, Any]) -> Task:
    return Task(
        id=data[StateKey.ID],
        title=data[StateKey.TITLE],
        status=TaskStatus(data[StateKey.STATUS]),
        current_step=data[StateKey.CURRENT_STEP],
        step_status=StepStatus(data[StateKey.STEP_STATUS]),
        loop_round=data[StateKey.LOOP_ROUND],
        branch=data[StateKey.BRANCH],
        history=tuple(
            HistoryEntry(
                at=entry[StateKey.AT],
                step=entry[StateKey.STEP],
                event=HistoryEvent(entry[StateKey.EVENT]),
            )
            for entry in data[StateKey.HISTORY]
        ),
    )


def state_to_dict(state: State) -> dict[str, Any]:
    return {
        StateKey.SCHEMA_VERSION: state.schema_version,
        StateKey.UPDATED_AT: state.updated_at,
        StateKey.ACTIVE_TASK_ID: state.active_task_id,
        StateKey.TASKS: [_task_to_dict(task) for task in state.tasks],
    }


def _task_to_dict(task: Task) -> dict[str, Any]:
    return {
        StateKey.ID: task.id,
        StateKey.TITLE: task.title,
        StateKey.STATUS: task.status,
        StateKey.CURRENT_STEP: task.current_step,
        StateKey.STEP_STATUS: task.step_status,
        StateKey.LOOP_ROUND: task.loop_round,
        StateKey.BRANCH: task.branch,
        StateKey.HISTORY: [
            {StateKey.AT: entry.at, StateKey.STEP: entry.step, StateKey.EVENT: entry.event}
            for entry in task.history
        ],
    }


# ------------------------------------------------------------------ config


@dataclass(frozen=True)
class WorkflowRef:
    """Where the workspace's workflow copy came from, and the sha256 it had when copied."""

    family: str
    source_path: str
    sha256: str


@dataclass(frozen=True)
class WorkspaceConfig:
    workflow: WorkflowRef
    schema_version: int = SCHEMA_VERSION


def config_from_dict(data: Mapping[str, Any]) -> WorkspaceConfig:
    ref = data[ConfigKey.WORKFLOW]
    return WorkspaceConfig(
        schema_version=data[ConfigKey.SCHEMA_VERSION],
        workflow=WorkflowRef(
            family=ref[ConfigKey.FAMILY],
            source_path=ref[ConfigKey.SOURCE_PATH],
            sha256=ref[ConfigKey.SHA256],
        ),
    )


def config_to_dict(config: WorkspaceConfig) -> dict[str, Any]:
    # Plain str keys/values so yaml.safe_dump can serialise them.
    return {
        str(ConfigKey.SCHEMA_VERSION): config.schema_version,
        str(ConfigKey.WORKFLOW): {
            str(ConfigKey.FAMILY): config.workflow.family,
            str(ConfigKey.SOURCE_PATH): config.workflow.source_path,
            str(ConfigKey.SHA256): config.workflow.sha256,
        },
    }


# ------------------------------------------------------------ engine/doctor


@dataclass(frozen=True)
class NextAction:
    kind: ActionKind
    step: Step | None = None
    loop_round: int | None = None


@dataclass(frozen=True)
class ProbeResult:
    returncode: int
    stdout: str


@dataclass(frozen=True)
class ToolCheck:
    tool: Tool
    status: ToolStatus
    required: bool
    version: str | None = None
    detail: str | None = None

    @property
    def install_url(self) -> str:
        return INSTALL_URLS[self.tool]


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[ToolCheck, ...]
    ok: bool
