import pytest

from agentflow import cli
from agentflow.cli import main
from agentflow.constants import ExitCode
from agentflow.doctor import ENGINE_NOT_RUNNING
from agentflow.models import ProbeResult


def test_version_prints_name_and_version(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "agentflow 0.1.0"


def test_no_command_prints_help_and_usage_code(capsys):
    assert main([]) == ExitCode.USAGE
    assert "usage:" in capsys.readouterr().out


class FakeProbe:
    def __init__(self, installed, engine_ok=True):
        self.installed, self.engine_ok = installed, engine_ok

    def which(self, name):
        return name if name in self.installed else None

    def run(self, args):
        if args[1] == "--version":
            return ProbeResult(0, f"{args[0]} 1.0\n")
        return ProbeResult(0 if self.engine_ok else 1, "")


@pytest.fixture
def probe(monkeypatch):
    def install(installed, engine_ok=True):
        monkeypatch.setattr(cli, "SystemToolProbe", lambda: FakeProbe(installed, engine_ok))

    return install


def test_doctor_all_ok(probe, capsys):
    probe({"uv", "git", "docker"})
    assert main(["doctor"]) == ExitCode.OK
    out = capsys.readouterr().out
    assert "[ok]" in out and "result: all required tools found" in out
    assert "https://podman.io/docs/installation" in out  # missing optional tool still shows its link


def test_doctor_missing_required(probe, capsys):
    probe({"git", "docker"})
    assert main(["doctor"]) == ExitCode.MISSING_REQUIREMENT
    out = capsys.readouterr().out
    assert "[missing] uv" in out
    assert "https://docs.astral.sh/uv/getting-started/installation/" in out


def test_doctor_without_container_runtime(probe, capsys):
    probe({"uv", "git"})
    assert main(["doctor"]) == ExitCode.MISSING_REQUIREMENT
    assert "install at least one of docker, podman" in capsys.readouterr().out


def test_doctor_engine_down_is_warning_only(probe, capsys):
    probe({"uv", "git", "docker"}, engine_ok=False)
    assert main(["doctor"]) == ExitCode.OK
    assert ENGINE_NOT_RUNNING in capsys.readouterr().out


def test_init_requires_workflow_option(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["init"])
    assert exc.value.code == ExitCode.USAGE


def test_init_creates_workspace(git_repo, workflow_file, monkeypatch, capsys):
    monkeypatch.chdir(git_repo)
    assert main(["init", "--workflow", str(workflow_file)]) == ExitCode.OK
    out = capsys.readouterr().out
    assert "workflow: sample (copied;" in out
    assert "git exclude: added .agentflow/" in out
    assert (git_repo / ".agentflow" / "state.json").is_file()


def test_init_twice_is_safe(git_repo, workflow_file, monkeypatch, capsys):
    monkeypatch.chdir(git_repo)
    main(["init", "--workflow", str(workflow_file)])
    capsys.readouterr()
    assert main(["init", "--workflow", str(workflow_file)]) == ExitCode.OK
    out = capsys.readouterr().out
    assert "created: nothing, workspace was complete" in out
    assert "git exclude: already excluded" in out


def test_init_outside_git_reports_error(tmp_path, workflow_file, monkeypatch, capsys):
    plain = tmp_path / "plain"
    plain.mkdir()
    monkeypatch.chdir(plain)
    assert main(["init", "--workflow", str(workflow_file)]) == ExitCode.NOT_GIT_REPO
    assert capsys.readouterr().err.startswith("error: not inside a git repository")


def test_init_warns_when_source_changed_since_copy(git_repo, workflow_file, monkeypatch, capsys):
    monkeypatch.chdir(git_repo)
    main(["init", "--workflow", str(workflow_file)])
    workflow_file.write_text(workflow_file.read_text(encoding="utf-8") + "\n# changed\n", encoding="utf-8")
    capsys.readouterr()
    assert main(["init", "--workflow", str(workflow_file)]) == ExitCode.OK
    assert "agentflow workflow sync" in capsys.readouterr().err
