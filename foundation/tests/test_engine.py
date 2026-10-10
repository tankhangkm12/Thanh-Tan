import pytest

from agentflow.constants import ActionKind, ExitCode, StepStatus, TaskStatus
from agentflow.engine import next_action
from agentflow.errors import AgentflowError
from agentflow.models import Task, workflow_from_dict


@pytest.fixture
def workflow(workflow_data):
    # Sample: confirm -> build -> check (on_fail: build), max 2 rounds.
    return workflow_from_dict(workflow_data)


def task(step="build", step_status=StepStatus.IN_PROGRESS, status=TaskStatus.OPEN, loop_round=0):
    return Task(
        id="T-001",
        title="t",
        status=status,
        current_step=step,
        step_status=step_status,
        loop_round=loop_round,
    )


def ids(action):
    return action.kind, (action.step.id if action.step else None), action.loop_round


def test_no_task_starts_at_first_step(workflow):
    assert ids(next_action(workflow, None)) == (ActionKind.START_TASK, "confirm", None)


@pytest.mark.parametrize("status", [TaskStatus.DONE, TaskStatus.CANCELLED])
def test_finished_task_means_start_a_new_one(workflow, status):
    assert next_action(workflow, task(status=status)).kind is ActionKind.START_TASK


def test_in_progress_continues(workflow):
    assert ids(next_action(workflow, task())) == (ActionKind.CONTINUE, "build", None)


def test_awaiting_approval(workflow):
    action = next_action(workflow, task("confirm", StepStatus.AWAITING_APPROVAL))
    assert ids(action) == (ActionKind.AWAIT_APPROVAL, "confirm", None)
    assert action.step.requires_approval is True


def test_passed_advances_along_main_path(workflow):
    assert ids(next_action(workflow, task("confirm", StepStatus.PASSED))) == (ActionKind.ADVANCE, "build", None)
    assert ids(next_action(workflow, task("build", StepStatus.PASSED))) == (ActionKind.ADVANCE, "check", None)


def test_passing_last_main_step_is_done(workflow):
    assert next_action(workflow, task("check", StepStatus.PASSED)).kind is ActionKind.DONE


def test_failure_goes_back_to_on_fail_and_counts_rounds(workflow):
    assert ids(next_action(workflow, task("check", StepStatus.FAILED, loop_round=0))) == (ActionKind.LOOP, "build", 1)
    assert ids(next_action(workflow, task("check", StepStatus.FAILED, loop_round=1))) == (ActionKind.LOOP, "build", 2)


def test_failure_after_max_rounds_blocks(workflow):
    assert ids(next_action(workflow, task("check", StepStatus.FAILED, loop_round=2))) == (
        ActionKind.BLOCKED,
        "check",
        2,
    )


def test_failure_without_on_fail_blocks(workflow):
    assert next_action(workflow, task("build", StepStatus.FAILED)).kind is ActionKind.BLOCKED


def test_blocked_task_stays_blocked(workflow):
    assert next_action(workflow, task(status=TaskStatus.BLOCKED)).kind is ActionKind.BLOCKED


def test_unknown_step_is_invalid_state(workflow):
    with pytest.raises(AgentflowError) as exc:
        next_action(workflow, task("ghost"))
    assert exc.value.code is ExitCode.INVALID_STATE
