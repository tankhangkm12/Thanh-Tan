import json
from pathlib import Path

import pytest

from agentflow.constants import ExitCode, GuardDecision, GuardRule
from agentflow.errors import AgentflowError
from agentflow.guard import evaluate, parse_request, split_commands, verdict_to_dict

CWD = Path("/work/repo")
OTHER = Path("/work/other")


class Branches:
    """Repo at CWD is on `current`; OTHER is on main. Known branches: main, develop, feature/x."""

    def __init__(self, current="feature/x"):
        self.current = {CWD: current, OTHER: "main"}

    def current_branch(self, directory):
        return self.current.get(directory)

    def branch_exists(self, directory, name):
        return name in {"main", "develop", "feature/x"}


def check(command, current="feature/x"):
    return evaluate(command, CWD, Branches(current))


DENIED = [
    # push in any form
    ("git push", GuardRule.PUSH),
    ("git push origin develop --force", GuardRule.PUSH),
    ("git -C sub push", GuardRule.PUSH),
    ("git -c core.editor=vi push", GuardRule.PUSH),
    ('"C:\\Program Files\\Git\\bin\\git.exe" push', GuardRule.PUSH),
    ("GIT.EXE push", GuardRule.PUSH),
    ("git status && git push", GuardRule.PUSH),
    ("git status; git push", GuardRule.PUSH),
    ("git status || git push", GuardRule.PUSH),
    ("git status\ngit push", GuardRule.PUSH),
    ("echo y | git push", GuardRule.PUSH),
    ("xargs git push < remotes", GuardRule.PUSH),
    ("if ($LASTEXITCODE -eq 0) { git push origin develop }", GuardRule.PUSH),
    ("& git push", GuardRule.PUSH),
    ("echo $(git push)", GuardRule.PUSH),
    ("x=`git push`", GuardRule.PUSH),
    ("bash -c 'git push origin'", GuardRule.PUSH),
    ('powershell -Command "git push"', GuardRule.PUSH),
    ("cmd /c git push", GuardRule.PUSH),
    ('sh -c "bash -c \\"git push\\""', GuardRule.PUSH),
    ('eval "git push"', GuardRule.PUSH),
    # reset --hard, anywhere
    ("git reset --hard", GuardRule.RESET_HARD),
    ("git reset --hard HEAD~1", GuardRule.RESET_HARD),
    ("git reset --hard HEAD@{1}", GuardRule.RESET_HARD),
    # clean with force and directories
    ("git clean -fd", GuardRule.CLEAN_FORCE_DIRS),
    ("git clean -df", GuardRule.CLEAN_FORCE_DIRS),
    ("git clean -fdx", GuardRule.CLEAN_FORCE_DIRS),
    ("git clean -f -d", GuardRule.CLEAN_FORCE_DIRS),
    ("git clean --force -d", GuardRule.CLEAN_FORCE_DIRS),
    # force-deleting branches
    ("git branch -D feature/x", GuardRule.BRANCH_FORCE_DELETE),
    ("git branch -d -f feature/x", GuardRule.BRANCH_FORCE_DELETE),
    ("git branch --delete --force feature/x", GuardRule.BRANCH_FORCE_DELETE),
    ("git branch -df feature/x", GuardRule.BRANCH_FORCE_DELETE),
    # deleting tags
    ("git tag -d v1", GuardRule.TAG_DELETE),
    ("git tag --delete v1", GuardRule.TAG_DELETE),
]


@pytest.mark.parametrize(("command", "rule"), DENIED)
def test_denied(command, rule):
    verdict = check(command)
    assert verdict.decision is GuardDecision.DENY, command
    assert verdict.rule is rule
    assert verdict.reason


@pytest.mark.parametrize("subcommand", ["commit -m x", "merge feature/x", "rebase main", "cherry-pick abc", "revert abc", "am p.patch"])
@pytest.mark.parametrize("branch", ["main", "develop"])
def test_committing_on_protected_branch_is_denied(subcommand, branch):
    verdict = check(f"git {subcommand}", current=branch)
    assert verdict.rule is GuardRule.PROTECTED_BRANCH
    assert f"'{branch}'" in verdict.reason


@pytest.mark.parametrize(
    "command",
    [
        "git switch develop && git merge feature/x",
        "git checkout main; git commit -m x",
        "git switch -c develop && git commit -m x",
        "git -C ../other commit -m x",
        "cd ../other && git commit -m x",
    ],
)
def test_switching_to_a_protected_branch_within_the_command_is_tracked(command):
    assert check(command).rule is GuardRule.PROTECTED_BRANCH


ALLOWED = [
    ("git status", "feature/x"),
    ("git commit -m 'add push support'", "feature/x"),
    ('git commit -m "docs: never git push; reset --hard"', "feature/x"),
    ("git merge develop", "feature/x"),
    ("git rebase develop", "feature/x"),
    ("git fetch origin", "develop"),
    ("git pull --ff-only", "develop"),
    ("git log --oneline | head", "main"),
    ("git reset --soft HEAD~1", "feature/x"),
    ("git reset HEAD file.txt", "feature/x"),
    ("git clean -n -d", "feature/x"),
    ("git clean -fx", "feature/x"),
    ("git branch -d feature/x", "develop"),
    ("git branch feature/y", "develop"),
    ("git tag v1", "develop"),
    ("git tag -l", "develop"),
    ("git merge --abort", "develop"),
    ("git rebase --abort", "main"),
    ("git switch feature/x && git commit -m x", "develop"),
    ("git checkout -b feature/y && git commit -m x", "develop"),
    ("git checkout -- src/app.py", "feature/x"),
    ("git checkout src/app.py && git commit -m x", "feature/x"),
    ("grep -r 'git push' docs", "main"),
    ("agentflow commit 'msg'", "feature/x"),
    ("uv run pytest", "main"),
    ("git", "main"),
    ("", "main"),
    ("git commit -m \"unbalanced", "feature/x"),
]


@pytest.mark.parametrize(("command", "current"), ALLOWED)
def test_allowed(command, current):
    verdict = check(command, current)
    assert verdict.decision is GuardDecision.ALLOW, (command, verdict.reason)
    assert verdict.rule is None


def test_unknown_branch_allows_commits():
    assert not check("git commit -m x", current=None).denied


def test_unbalanced_quotes_still_find_push():
    assert check('git push "origin').rule is GuardRule.PUSH


def test_split_commands_respects_quotes():
    assert split_commands('git commit -m "a; b && c" && git status') == [
        ["git", "commit", "-m", "a; b && c"],
        ["git", "status"],
    ]


def test_parse_request_and_output():
    request = parse_request(json.dumps({"command": "git push", "cwd": "/x"}))
    assert request.command == "git push" and request.cwd == Path("/x")
    assert parse_request('{"command": "ls"}').cwd is None
    verdict = check("git push")
    out = json.loads(json.dumps(verdict_to_dict(verdict)))
    assert out == {"decision": "deny", "rule": "push", "reason": verdict.reason}


@pytest.mark.parametrize("text", ["not json", "[]", '{"cwd": "/x"}', '{"command": 1}', '{"command": "ls", "cwd": 3}'])
def test_parse_request_rejects_bad_input(text):
    with pytest.raises(AgentflowError) as exc:
        parse_request(text)
    assert exc.value.code is ExitCode.INVALID_INPUT
