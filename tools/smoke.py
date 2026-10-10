"""End-to-end smoke test of the installed `agentflow` on a throw-away git repository.

    uv run tools/smoke.py

Everything happens in a temporary directory; no other repository is touched. Needs `agentflow` on PATH
(see the README), git, and a running Docker or Podman engine for the Gitleaks scan.
"""

import json
import os
import secrets
import shutil
import stat
import string
import subprocess
import sys
import tempfile
from pathlib import Path

ENCODING = "utf-8"
AGENTFLOW = "agentflow"
WORKFLOW = Path(__file__).resolve().parents[1] / "families" / "software-dev" / "core" / "workflow.yaml"
MAIN, DEVELOP = "main", "develop"
TASK_ID = "T-001"
STEP_TIMEOUT = 900
# A made-up GitHub-style token; the random part is generated at run time.
FAKE_TOKEN_PREFIX = "ghp" + "_"
FAKE_TOKEN_LENGTH = 36


class Failure(Exception):
    pass


def run(args: list[str], cwd: Path, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args, cwd=cwd, input=stdin, capture_output=True, text=True, encoding=ENCODING, timeout=STEP_TIMEOUT, check=False
    )


def expect(condition: bool, what: str, detail: str = "") -> None:
    print(f"{'ok  ' if condition else 'FAIL'} {what}")
    if not condition:
        raise Failure(f"{what}\n{detail}")


class Session:
    def __init__(self, repo: Path) -> None:
        self.repo = repo

    def git(self, *args: str) -> str:
        done = run(["git", *args], self.repo)
        if done.returncode != 0:
            raise Failure(f"git {' '.join(args)} failed: {done.stderr}")
        return done.stdout.strip()

    def af(self, *args: str, stdin: str | None = None, ok: bool = True) -> subprocess.CompletedProcess[str]:
        done = run([AGENTFLOW, *args], self.repo, stdin)
        expect((done.returncode == 0) is ok, f"agentflow {' '.join(args)} -> exit {done.returncode}", done.stdout + done.stderr)
        return done


def fake_token_body() -> str:
    """Random characters, so no token-looking string is ever stored in this repository."""
    return "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(FAKE_TOKEN_LENGTH))


def _make_writable_and_retry(function, path, _excinfo) -> None:
    # git object files are read-only, which Windows refuses to delete.
    os.chmod(path, stat.S_IWRITE)
    function(path)


def main() -> int:
    if shutil.which(AGENTFLOW) is None or shutil.which("git") is None:
        print("agentflow and git must be on PATH (see README: uv tool install)", file=sys.stderr)
        return 2
    base = Path(tempfile.mkdtemp(prefix="agentflow-smoke-"))
    repo = base / "sample"
    repo.mkdir()
    env = {"GIT_CEILING_DIRECTORIES": str(base)}
    os.environ.update(env)
    try:
        s = Session(repo)
        s.git("init", "-q", "-b", MAIN)
        for key, value in {"user.name": "Smoke", "user.email": "smoke@example.invalid", "commit.gpgsign": "false"}.items():
            s.git("config", key, value)
        (repo / "README.md").write_text("sample\n", encoding=ENCODING)
        s.git("add", "README.md")
        s.git("commit", "-q", "-m", "initial")
        s.git("switch", "-q", "-c", DEVELOP)

        s.af("init", "--workflow", str(WORKFLOW))
        s.af("task", "new", "Add a greeting", "--type", "feature")
        branch = s.git("branch", "--show-current")
        expect(branch == f"feature/{TASK_ID}-add-a-greeting", "task branch name", branch)

        s.af("task", "advance", "--result", "pass")
        s.af("task", "advance", "--result", "pass", ok=False)  # confirm now waits for approval
        s.af("report", "--step", "confirm", stdin="# Confirmed\n")
        s.af("task", "approve")  # confirm -> plan
        s.af("task", "advance", "--result", "pass")
        s.af("task", "approve")  # plan -> implement

        (repo / "greeting.txt").write_text("hello\n", encoding=ENCODING)
        s.git("add", "greeting.txt")
        done = s.af("commit", "add greeting")
        expect(s.git("log", "-1", "--format=%s") == f"{TASK_ID}: add greeting", "commit has the task prefix")
        expect("committed" in done.stdout, "commit reports success")

        s.af("task", "advance", "--result", "pass")  # implement -> test
        s.af("task", "advance", "--result", "fail")  # test fails -> back to implement, round 1
        status = s.af("status").stdout
        expect("step 'implement'" in status and "rework rounds: 1/3" in status, "fail goes back to implement", status)
        for _ in range(3):  # implement, test, security
            s.af("task", "advance", "--result", "pass")
        s.af("task", "advance", "--result", "pass")  # review passes -> awaiting approval
        s.af("task", "approve")
        state = json.loads((repo / ".agentflow" / "state.json").read_text(encoding=ENCODING))
        expect(state["tasks"][0]["status"] == "done" and state["active_task_id"] is None, "task is done after review approval")

        s.af("task", "new", "Second task")
        s.af("task", "cancel")

        secret_file = repo / "leak.txt"
        s.af("task", "new", "Leak check")
        secret_file.write_text(f'token = "{FAKE_TOKEN_PREFIX}{fake_token_body()}"\n', encoding=ENCODING)
        s.git("add", "leak.txt")
        before = s.git("rev-parse", "HEAD")
        s.af("commit", "should be blocked", ok=False)
        expect(s.git("rev-parse", "HEAD") == before, "a staged secret blocks the commit")
        s.git("reset", "-q")
        secret_file.unlink()
        s.af("task", "cancel")
        s.git("switch", "-q", DEVELOP)

        guard = json.loads(s.af("guard", stdin=json.dumps({"command": "git push origin develop", "cwd": str(repo)})).stdout)
        expect(guard["decision"] == "deny" and guard["rule"] == "push", "guard blocks git push", str(guard))
        allowed = json.loads(s.af("guard", stdin=json.dumps({"command": "git status", "cwd": str(repo)})).stdout)
        expect(allowed["decision"] == "allow", "guard allows git status")
        on_develop = json.loads(s.af("guard", stdin=json.dumps({"command": "git commit -m x", "cwd": str(repo)})).stdout)
        expect(on_develop["rule"] == "protected-branch", "guard blocks committing on develop")

        claude = s.af("hook", "pre-tool", "--cli", "claude", stdin=json.dumps({"cwd": str(repo), "tool_input": {"command": "git push"}}))
        expect(json.loads(claude.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny", "claude pre-tool hook denies push")
        agy = s.af(
            "hook",
            "pre-tool",
            "--cli",
            "antigravity",
            stdin=json.dumps({"workspacePaths": [str(repo)], "toolCall": {"name": "run_command", "args": {"CommandLine": "git push"}}}),
        )
        expect(json.loads(agy.stdout)["decision"] == "deny", "antigravity pre-tool hook denies push")
        summary = s.af("hook", "session-start", "--cli", "claude", stdin=json.dumps({"cwd": str(repo)}))
        expect("agentflow workspace found" in summary.stdout, "session-start hook prints the summary")

        bare = base / "no-workspace"
        bare.mkdir()
        run(["git", "init", "-q"], bare)
        silent = run([AGENTFLOW, "hook", "pre-tool", "--cli", "claude"], bare, json.dumps({"cwd": str(bare), "tool_input": {"command": "git push"}}))
        expect(silent.returncode == 0 and silent.stdout == "", "hooks do nothing without .agentflow/")

        print("\nsmoke test passed")
        return 0
    except Failure as exc:
        print(f"\nsmoke test FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        shutil.rmtree(base, onerror=_make_writable_and_retry)


if __name__ == "__main__":
    sys.exit(main())
