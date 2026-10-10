"""What agentflow does when a CLI fires a hook.

Hooks must never get in the way: a project without ``.agentflow/``, unreadable input or an unreadable
state all end in "no output", which every CLI treats as "carry on".
"""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from agentflow.constants import (
    ANTIGRAVITY_FIRST_INVOCATION,
    CliKind,
    HookEvent,
    ReplyKind,
    StepStatus,
    TaskStatus,
)
from agentflow.engine import next_action
from agentflow.errors import AgentflowError
from agentflow.guard import evaluate
from agentflow.hook_adapters import ADAPTERS
from agentflow.interfaces import BranchLookup
from agentflow.models import HookInput, HookReply, State, Workflow
from agentflow.render import NONE_TEXT, describe_action, describe_step
from agentflow.state import JsonStateStore
from agentflow.workspace import WorkspacePaths, find_workspace, load_workspace_workflow

RULES_TEXT = (
    "Rules: change task state only through `agentflow task ...`; save step reports with "
    "`agentflow report --step <id>`; commit with `agentflow commit`; never edit files under .agentflow/ "
    "by hand; never push."
)
NO_TASK_TEXT = "No active task. To begin, use the start skill (it runs `agentflow task new`)."
STOP_REMINDER = (
    "agentflow: task {task} is still at step '{step}'. If that step is finished, record it with "
    "`agentflow task advance --result pass|fail` (and `agentflow report --step {step}`); "
    "if it is waiting for you, use `agentflow task approve`."
)


def handle_hook(event: HookEvent, cli: CliKind, stdin_text: str, branches: BranchLookup) -> str:
    """Return the text to print on stdout (possibly empty)."""
    adapter = ADAPTERS[cli]
    payload = _parse(stdin_text)
    if payload is None:
        return ""
    hook_input = adapter.read(event, payload)
    paths = _workspace(hook_input.cwd)
    if paths is None:
        return ""
    reply = _reply(event, cli, hook_input, paths, branches)
    return adapter.render(event, reply)


def _parse(text: str) -> Mapping[str, Any] | None:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _workspace(cwd: Path | None) -> WorkspacePaths | None:
    if cwd is None:
        return None
    try:
        return find_workspace(cwd)
    except AgentflowError:  # not a git repository, or no .agentflow/ in it
        return None


def _reply(event: HookEvent, cli: CliKind, hook_input: HookInput, paths: WorkspacePaths, branches: BranchLookup) -> HookReply:
    match event:
        case HookEvent.PRE_TOOL:
            return _guard_reply(hook_input, branches)
        case HookEvent.SESSION_START:
            if cli is CliKind.ANTIGRAVITY and hook_input.invocation_num != ANTIGRAVITY_FIRST_INVOCATION:
                return HookReply()
            return _loaded(paths, _summary)
        case HookEvent.STOP:
            if hook_input.stop_hook_active:
                return HookReply()
            return _loaded(paths, _reminder, kind=ReplyKind.REMINDER)
    return HookReply()


def _guard_reply(hook_input: HookInput, branches: BranchLookup) -> HookReply:
    if not hook_input.command or hook_input.cwd is None:
        return HookReply()
    verdict = evaluate(hook_input.command, hook_input.cwd, branches)
    return HookReply(ReplyKind.DENY, verdict.reason or "") if verdict.denied else HookReply()


def _loaded(paths: WorkspacePaths, build, kind: ReplyKind = ReplyKind.CONTEXT) -> HookReply:
    """Load workflow and state, then let ``build`` write the text; any agentflow error means no reply."""
    try:
        workflow = load_workspace_workflow(paths)
        state = JsonStateStore(paths.dir, workflow).load()
    except AgentflowError:
        return HookReply()
    text = build(workflow, state)
    return HookReply(kind, text) if text else HookReply()


def _summary(workflow: Workflow, state: State) -> str:
    task = state.active_task()
    lines = [f"agentflow workspace found (workflow: {workflow.family})."]
    if task is None:
        lines.append(NO_TASK_TEXT)
    else:
        step = workflow.get_step(task.current_step)
        lines += [
            f"Active task: {task.id} {task.title} (branch {task.branch or NONE_TEXT}, status {task.status}).",
            f"Current step: {describe_step(step) if step else task.current_step}, {task.step_status}.",
            f"Next: {describe_action(next_action(workflow, task))}.",
        ]
    lines.append(RULES_TEXT)
    return "\n".join(lines)


def _reminder(workflow: Workflow, state: State) -> str:
    task = state.active_task()
    if task is None or task.status is not TaskStatus.OPEN or task.step_status is not StepStatus.IN_PROGRESS:
        return ""
    return STOP_REMINDER.format(task=task.id, step=task.current_step)
