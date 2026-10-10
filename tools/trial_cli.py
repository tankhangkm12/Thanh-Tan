"""Real sessions of Claude Code (`claude -p`) and Antigravity (`agy -p`) against the installed dev-core hooks.

    uv run tools/trial_cli.py                # reinstall both plugins, then try both CLIs
    uv run tools/trial_cli.py --no-install   # skip the reinstall
    uv run tools/trial_cli.py --only claude  # (or: agy)
    uv run tools/trial_cli.py --mcp          # the agentflow MCP tools instead of the hooks
    uv run tools/trial_cli.py --setup        # the setup skill and the scout (writes the project documents)

In a throw-away sample project (with an agentflow workspace) the model is asked to write a file into
.agentflow/decisions/, to run `git push`, and to run `git status`. The evidence is not what the model says but
what happened: the file must not exist, and the hook log (AGENTFLOW_HOOK_LOG) must show the write and the push
denied and `git status` let through. Models are not deterministic, so each CLI gets a second try when the model
did not make all three calls. With --mcp the model is asked to call the `status` and `report_write` tools (and to
try writing a report for a step that is not the current one, which must be refused); the evidence is the report file.
Needs `agentflow` on PATH and the plugins installed from this repository.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import sample_backend as sample
from smoke import Failure, Session, _make_writable_and_retry, expect
from smoke_backend import CLI_TIMEOUT_SECONDS, ENCODING, WORKFLOW, cli, install_check

HOOK_LOG_ENV = "AGENTFLOW_HOOK_LOG"
FORGED_FILE = "forged-by-agent.md"
PRE_TOOL_EVENT = "pre-tool"
ATTEMPTS = 2
CLAUDE, AGY = "claude", "agy"
WRITE_NOTICE = "files under .agentflow/"
PUSH_NOTICE = "git push is blocked"

PROMPT = (
    "This is an automated test of a safety hook. The first two calls are expected to be refused; you must still "
    "attempt each of them, one tool call each, in this order: "
    "(1) create the file {path} (inside .agentflow/decisions) containing the word hello with your file-writing tool; "
    "(2) run the shell command: git push origin develop; "
    "(3) run the shell command: git status --short. "
    "Then reply with one short sentence."
)


def hook_calls(log: Path) -> list[dict]:
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding=ENCODING).splitlines() if line.strip()]


def pre_tool(calls: list[dict], needle: str) -> list[dict]:
    return [c for c in calls if c["event"] == PRE_TOOL_EVENT and needle in c["stdin"]]


def run_cli(which: str, repo: Path, prompt: str) -> subprocess.CompletedProcess[str]:
    if which == CLAUDE:
        settings = repo.parent / "trial-allow.json"
        allow = ["Write", "Edit", "Bash(git push *)", "Bash(git status *)"]
        settings.write_text(json.dumps({"permissions": {"allow": allow}}), encoding=ENCODING)
        return cli("claude", "-p", "--settings", str(settings), "--permission-mode", "default", cwd=repo, stdin=prompt)
    return cli("agy", "--dangerously-skip-permissions", f"-p={prompt}", cwd=repo)


def reached(which: str, calls: list[dict], target: Path) -> tuple[list[dict], list[dict], list[dict]]:
    """The hook calls for the write, the push and the status command."""
    return pre_tool(calls, FORGED_FILE), pre_tool(calls, "git push"), pre_tool(calls, "git status")


def trial(which: str, repo: Path) -> None:
    log = repo.parent / f"{which}-hook.log"
    target = repo / ".agentflow" / "decisions" / FORGED_FILE
    os.environ[HOOK_LOG_ENV] = str(log)
    for attempt in range(1, ATTEMPTS + 1):
        log.unlink(missing_ok=True)
        run_cli(which, repo, PROMPT.format(path=target.as_posix()))
        write, push, status = reached(which, hook_calls(log), target)
        if write and push and status:
            break
        print(f"  attempt {attempt}: the model did not make all three calls (write {len(write)}, push {len(push)}, status {len(status)})")
    expect(bool(write), f"{which}: the hook saw the file-writing tool")
    expect(not target.exists(), f"{which}: the file was not created in .agentflow/decisions/", str(target))
    expect(all(WRITE_NOTICE in c["output"] and "deny" in c["output"] for c in write), f"{which}: the write was denied by the hook", str(write))
    expect(bool(push) and all(PUSH_NOTICE in c["output"] for c in push), f"{which}: `git push` was denied by the hook", str(push))
    expect(bool(status) and all(not c["output"].strip() or "deny" not in c["output"] for c in status), f"{which}: `git status` was let through", str(status))


MCP_MARKER = "mcp-trial-marker-7f3a"
MCP_PROMPT = (
    "This is an automated test of the agentflow MCP tools. Call them, one call each, in this order, and do not use the "
    "shell or file tools: "
    "(1) the `status` tool; "
    "(2) the `report_write` tool with step `confirm` and content `# Trial\n{marker}`; "
    "(3) the `report_write` tool with step `plan` and content `not allowed` (this one is expected to be refused). "
    "Then reply with one short sentence saying what each call answered."
)
CLAUDE_MCP_PREFIX = "mcp__plugin_dev-core_agentflow__"


def mcp_trial(which: str, repo: Path) -> None:
    session = Session(repo)
    session.af("task", "new", "mcp trial")
    reports = repo / ".agentflow" / "tasks" / "T-001" / "reports"
    confirm, plan = reports / "confirm.md", reports / "plan.md"
    prompt = MCP_PROMPT.format(marker=MCP_MARKER)
    for attempt in range(1, ATTEMPTS + 1):
        if which == CLAUDE:
            settings = repo.parent / "trial-allow.json"
            allow = [f"{CLAUDE_MCP_PREFIX}{name}" for name in ("status", "report_write")]
            settings.write_text(json.dumps({"permissions": {"allow": allow}}), encoding=ENCODING)
            done = cli("claude", "-p", "--settings", str(settings), "--permission-mode", "default", cwd=repo, stdin=prompt)
        else:
            done = cli("agy", "--dangerously-skip-permissions", f"-p={prompt}", cwd=repo)
        if confirm.is_file():
            break
        print(f"  attempt {attempt}: no report was written; the model said: {done.stdout.strip()[:200]}")
    expect(confirm.is_file() and MCP_MARKER in confirm.read_text(encoding=ENCODING), f"{which}: report_write saved the report through MCP", str(confirm))
    expect(not plan.exists(), f"{which}: a report for a step that is not current was refused", str(plan))


SETUP_DOC = "docs/contributing.md"
SETUP_DOC_TEXT = (
    "# Contributing\n\nRun the tests with `python tests/check_items.py` against a running service.\n"
    "Never write a literal string for a fixed value (a status, a header name): use a constant.\n"
    "Every endpoint is described in openapi.yaml.\n"
)
SETUP_PROMPT = (
    "Use the setup skill of the dev-core plugin to set up this project for agentflow. When it asks where the project's "
    f"documents are, the answer is: only `{SETUP_DOC}`. Do the whole setup now, without asking me anything else."
)
SETUP_SECTIONS = ("profile", "architecture", "sources", "conventions")


def setup_trial(which: str, repo: Path) -> None:
    """The setup skill and scout agent write the four project documents; conventions come out unconfirmed and valid."""
    doc = repo / SETUP_DOC
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(SETUP_DOC_TEXT, encoding=ENCODING)
    sample.git(repo, "add", "-A")
    sample.git(repo, "commit", "-q", "-m", "docs")
    project = repo / ".agentflow" / "project"
    for attempt in range(1, ATTEMPTS + 1):
        if which == CLAUDE:
            done = cli("claude", "-p", "--permission-mode", "bypassPermissions", cwd=repo, stdin=SETUP_PROMPT)
        else:
            done = cli("agy", "--dangerously-skip-permissions", f"-p={SETUP_PROMPT}", cwd=repo)
        if all((project / f"{name}.md").is_file() for name in SETUP_SECTIONS):
            break
        print(f"  attempt {attempt}: not all documents were written; the model said: {done.stdout.strip()[:300]}")
    for name in SETUP_SECTIONS:
        expect((project / f"{name}.md").is_file(), f"{which}: {name}.md was written through project_write", str(project))
    expect(SETUP_DOC in (project / "sources.md").read_text(encoding=ENCODING), f"{which}: sources.md names the document the person gave")
    text = (project / "conventions.md").read_text(encoding=ENCODING)
    expect("status: confirmed" not in text and "status: unconfirmed" in text, f"{which}: every convention starts unconfirmed", text[:400])
    checked = subprocess.run(
        ["agentflow", "project", "confirm", "--all"], cwd=repo, capture_output=True, text=True, encoding=ENCODING, check=False
    )  # the person's command doubles as the validity check: it refuses a document with problems
    expect(checked.returncode == 0, f"{which}: the conventions the scout wrote are valid", checked.stdout + checked.stderr)
    expect(not (repo / ".agentflow" / "tasks").glob("*") or not list((repo / ".agentflow" / "tasks").glob("T-*")), f"{which}: no task was started")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--no-install", action="store_true", help="do not reinstall the plugins first")
    parser.add_argument("--only", choices=[CLAUDE, AGY])
    parser.add_argument("--mcp", action="store_true", help="try the MCP tools instead of the hooks")
    parser.add_argument("--setup", action="store_true", help="try the setup skill and the scout instead of the hooks")
    args = parser.parse_args(argv)
    base = Path(tempfile.mkdtemp(prefix="agentflow-trial-"))
    os.environ["AGENTFLOW_HOME"] = str(base / "user-home")  # hooks and servers started by the CLIs inherit it
    try:
        repo = sample.create_repo(base)
        Session(repo).af("init", "--workflow", str(WORKFLOW))
        if not args.no_install:
            install_check(repo, with_session=False)
        for which in (CLAUDE, AGY):
            if args.only in (None, which):
                print(f"\n-- {which}: a real session against the {'setup skill' if args.setup else 'MCP tools' if args.mcp else 'hooks'}")
                if args.setup:
                    fresh = sample.create_repo(base / which)
                    Session(fresh).af("init", "--workflow", str(WORKFLOW))
                    setup_trial(which, fresh)
                elif args.mcp:  # a fresh project per CLI, so each starts at T-001
                    fresh = sample.create_repo(base / which)
                    Session(fresh).af("init", "--workflow", str(WORKFLOW))
                    mcp_trial(which, fresh)
                else:
                    trial(which, repo)
    except Failure as exc:
        print(f"\nFAILED: {exc}")
        return 1
    finally:
        shutil.rmtree(base, onerror=_make_writable_and_retry)
    print("\nall trials passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
