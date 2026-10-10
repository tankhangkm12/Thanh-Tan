"""The hooks dev-core declares must call `agentflow hook` with arguments the CLI accepts."""

import json
import shlex
from pathlib import Path

import pytest

from agentflow.cli import build_parser
from agentflow.constants import PACKAGE_NAME, CliKind, Command, HookEvent

CORE = Path(__file__).resolve().parents[2] / "families" / "software-dev" / "core"
CLAUDE_HOOKS = CORE / "hooks" / "hooks.json"
ANTIGRAVITY_HOOKS = CORE / "hooks.json"

pytestmark = pytest.mark.skipif(not CORE.is_dir(), reason="plugin sources are not next to foundation/")


def claude_argvs() -> list[list[str]]:
    data = json.loads(CLAUDE_HOOKS.read_text(encoding="utf-8"))
    return [
        [hook["command"], *hook["args"]]
        for groups in data["hooks"].values()
        for group in groups
        for hook in group["hooks"]
    ]


def antigravity_argvs() -> list[list[str]]:
    data = json.loads(ANTIGRAVITY_HOOKS.read_text(encoding="utf-8"))
    argvs = []
    for events in data.values():
        for handlers in events.values():
            for handler in handlers:
                nested = handler.get("hooks", [handler])
                argvs += [shlex.split(item["command"]) for item in nested]
    return argvs


@pytest.mark.parametrize(("argvs", "cli"), [(claude_argvs, CliKind.CLAUDE), (antigravity_argvs, CliKind.ANTIGRAVITY)])
def test_every_declared_hook_is_a_valid_agentflow_call(argvs, cli):
    calls = argvs()
    parser = build_parser()
    seen = set()
    for argv in calls:
        assert argv[0] == PACKAGE_NAME
        args = parser.parse_args(argv[1:])
        assert args.command == Command.HOOK and args.cli is cli
        seen.add(args.event)
    assert seen == set(HookEvent)


def test_claude_pre_tool_matcher_covers_both_shell_tools():
    data = json.loads(CLAUDE_HOOKS.read_text(encoding="utf-8"))
    assert data["hooks"]["PreToolUse"][0]["matcher"] == "Bash|PowerShell"


def test_antigravity_pre_tool_matcher_is_run_command():
    data = json.loads(ANTIGRAVITY_HOOKS.read_text(encoding="utf-8"))
    assert data["agentflow"]["PreToolUse"][0]["matcher"] == "run_command"
