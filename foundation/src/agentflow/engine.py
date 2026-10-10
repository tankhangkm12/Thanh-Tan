"""Decide what comes next for a task, from the workflow and the task's state. Pure: no I/O."""

from agentflow.constants import ActionKind, ExitCode, StepKind, StepStatus, TaskStatus
from agentflow.errors import AgentflowError
from agentflow.models import NextAction, Task, Workflow

_FINISHED = frozenset({TaskStatus.DONE, TaskStatus.CANCELLED})


def next_action(workflow: Workflow, task: Task | None) -> NextAction:
    if task is None or task.status in _FINISHED:
        return NextAction(ActionKind.START_TASK, workflow.first_step())

    step = workflow.get_step(task.current_step)
    if step is None:
        raise AgentflowError(
            f"task {task.id} is at step '{task.current_step}', which the workflow does not define",
            ExitCode.INVALID_STATE,
        )
    if task.status is TaskStatus.BLOCKED:
        return NextAction(ActionKind.BLOCKED, step, task.loop_round)

    match task.step_status:
        case StepStatus.IN_PROGRESS:
            return NextAction(ActionKind.CONTINUE, step)
        case StepStatus.AWAITING_APPROVAL:
            return NextAction(ActionKind.AWAIT_APPROVAL, step)
        case StepStatus.PASSED:
            return _after_pass(workflow, step.id)
        case StepStatus.FAILED:
            return _after_fail(workflow, task)
    raise AssertionError(task.step_status)  # unreachable: StepStatus is exhaustive


def _after_pass(workflow: Workflow, step_id: str) -> NextAction:
    step = workflow.get_step(step_id)
    assert step is not None
    if step.kind is StepKind.LOOP:
        assert step.loop is not None
        return NextAction(ActionKind.ADVANCE, workflow.get_step(step.loop.back_to))
    following = workflow.step_after(step_id)
    if following is None:
        return NextAction(ActionKind.DONE)
    return NextAction(ActionKind.ADVANCE, following)


def _after_fail(workflow: Workflow, task: Task) -> NextAction:
    step = workflow.get_step(task.current_step)
    assert step is not None
    # A failed loop step, or a step with nowhere to go on failure, needs a person.
    if step.kind is StepKind.LOOP or step.on_fail is None:
        return NextAction(ActionKind.BLOCKED, step, task.loop_round)
    loop_step = workflow.get_step(step.on_fail)
    assert loop_step is not None and loop_step.loop is not None
    if task.loop_round >= loop_step.loop.max_rounds:
        return NextAction(ActionKind.BLOCKED, step, task.loop_round)
    return NextAction(ActionKind.LOOP, loop_step, task.loop_round + 1)
