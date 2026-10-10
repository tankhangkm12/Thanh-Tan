"""Hook payloads and replies in the formats each CLI documents.

Claude Code: https://code.claude.com/docs (hooks reference). Antigravity: the ``hooks.md`` page of its
bundled customization docs. Keys are camelCase in Antigravity and snake_case in Claude Code.
"""

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from agentflow.constants import (
    ANTIGRAVITY_PRE_TOOL_PASS_OUTPUT,
    EMPTY_JSON_OBJECT,
    AntigravityDecision,
    AntigravityHookKey,
    ClaudeHookKey,
    ClaudeHookValue,
    CliKind,
    HookEvent,
    ReplyKind,
)
from agentflow.interfaces import HookAdapter
from agentflow.models import HookInput, HookReply


def _dump(data: Mapping[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _path(value: Any) -> Path | None:
    return Path(value) if isinstance(value, str) and value else None


class ClaudeAdapter:
    def read(self, event: HookEvent, payload: Mapping[str, Any]) -> HookInput:
        command = _mapping(payload.get(ClaudeHookKey.TOOL_INPUT)).get(ClaudeHookKey.COMMAND)
        return HookInput(
            cwd=_path(payload.get(ClaudeHookKey.CWD)),
            command=command if isinstance(command, str) else None,
            stop_hook_active=payload.get(ClaudeHookKey.STOP_HOOK_ACTIVE) is True,
        )

    def render(self, event: HookEvent, reply: HookReply) -> str:
        match event, reply.kind:
            case HookEvent.PRE_TOOL, ReplyKind.DENY:
                return _dump(
                    {
                        ClaudeHookKey.HOOK_SPECIFIC_OUTPUT: {
                            ClaudeHookKey.HOOK_EVENT_NAME: ClaudeHookValue.PRE_TOOL_USE,
                            ClaudeHookKey.PERMISSION_DECISION: ClaudeHookValue.DENY,
                            ClaudeHookKey.PERMISSION_DECISION_REASON: reply.text,
                        }
                    }
                )
            case HookEvent.SESSION_START, ReplyKind.CONTEXT:
                return _dump(
                    {
                        ClaudeHookKey.HOOK_SPECIFIC_OUTPUT: {
                            ClaudeHookKey.HOOK_EVENT_NAME: ClaudeHookValue.SESSION_START,
                            ClaudeHookKey.ADDITIONAL_CONTEXT: reply.text,
                        }
                    }
                )
            case HookEvent.STOP, ReplyKind.REMINDER:
                # Shown to the person without stopping or restarting the turn.
                return _dump({ClaudeHookKey.SYSTEM_MESSAGE: reply.text})
        return ""


class AntigravityAdapter:
    def read(self, event: HookEvent, payload: Mapping[str, Any]) -> HookInput:
        args = _mapping(_mapping(payload.get(AntigravityHookKey.TOOL_CALL)).get(AntigravityHookKey.ARGS))
        command = args.get(AntigravityHookKey.COMMAND_LINE)
        workspaces = payload.get(AntigravityHookKey.WORKSPACE_PATHS)
        first_workspace = _path(workspaces[0]) if isinstance(workspaces, list) and workspaces else None
        number = payload.get(AntigravityHookKey.INVOCATION_NUM)
        return HookInput(
            # The hook process runs in the plugin directory, so the project comes from the payload.
            cwd=_path(args.get(AntigravityHookKey.CWD)) or first_workspace,
            command=command if isinstance(command, str) else None,
            invocation_num=number if isinstance(number, int) and not isinstance(number, bool) else None,
        )

    def render(self, event: HookEvent, reply: HookReply) -> str:
        match event, reply.kind:
            case HookEvent.PRE_TOOL, ReplyKind.DENY:
                return _dump(
                    {
                        AntigravityHookKey.DECISION: AntigravityDecision.DENY,
                        AntigravityHookKey.REASON: reply.text,
                    }
                )
            case HookEvent.PRE_TOOL, _:
                return ANTIGRAVITY_PRE_TOOL_PASS_OUTPUT
            case HookEvent.SESSION_START, ReplyKind.CONTEXT:
                return _dump({AntigravityHookKey.INJECT_STEPS: [{AntigravityHookKey.EPHEMERAL_MESSAGE: reply.text}]})
            case HookEvent.SESSION_START, _:
                return EMPTY_JSON_OBJECT
            case HookEvent.STOP, _:
                # Stop can only block or allow; there is no way to remind without blocking.
                return _dump({AntigravityHookKey.DECISION: AntigravityDecision.ALLOW_STOP})
        return ""


ADAPTERS: dict[CliKind, HookAdapter] = {
    CliKind.CLAUDE: ClaudeAdapter(),
    CliKind.ANTIGRAVITY: AntigravityAdapter(),
}
