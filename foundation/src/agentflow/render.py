"""Human-readable text for steps and next actions, shared by STATE.md and the CLI."""

from agentflow.constants import ActionKind
from agentflow.models import NextAction, Step

NONE_TEXT = "none"
APPROVAL_NOTE = ", needs approval"

_ACTION_TEXT = {
    ActionKind.START_TASK: "start a new task at {step}",
    ActionKind.CONTINUE: "continue {step}",
    ActionKind.AWAIT_APPROVAL: "wait for a person to approve {step}",
    ActionKind.ADVANCE: "move on to {step}",
    ActionKind.LOOP: "fix the failure in {step}, round {round}/{max_rounds}",
    ActionKind.BLOCKED: "blocked at {step}: a person has to decide how to continue",
    ActionKind.DONE: "all steps passed: the task can be closed",
}


def describe_step(step: Step) -> str:
    approval = APPROVAL_NOTE if step.requires_approval else ""
    return f"step '{step.id}' ({step.name}; role {step.role}{approval})"


def describe_action(action: NextAction) -> str:
    max_rounds = action.step.loop.max_rounds if action.step and action.step.loop else None
    return _ACTION_TEXT[action.kind].format(
        step=describe_step(action.step) if action.step else NONE_TEXT,
        round=action.loop_round,
        max_rounds=max_rounds,
    )
