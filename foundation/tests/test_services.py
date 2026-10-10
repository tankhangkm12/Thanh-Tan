import pytest
from conftest import SAMPLE_WORKFLOW, write_workflow

from agentflow.cli import main
from agentflow.constants import ActionKind, ExitCode, ProjectSection
from agentflow.errors import AgentflowError
from agentflow.interfaces import WorkspaceService
from agentflow.services import WorkspaceServices
from agentflow.workspace import find_workspace

GOOD_PLAN = """### C1 - Build it
- role: builder
- done-when: `pytest`
- docs: không có — internal change
"""


@pytest.fixture
def repo(gitflow_repo, tmp_path, monkeypatch, capsys):
    data = {**SAMPLE_WORKFLOW, "steps": [dict(step) for step in SAMPLE_WORKFLOW["steps"]]}
    data["steps"][1]["gates"] = ["plan-valid"]  # the "build" step plays the plan step
    path = write_workflow(tmp_path / "plugin" / "workflow.yaml", data)
    monkeypatch.chdir(gitflow_repo)
    assert main(["init", "--workflow", str(path)]) == ExitCode.OK
    capsys.readouterr()
    return gitflow_repo


@pytest.fixture
def service(repo):
    return WorkspaceServices(find_workspace(repo))


def refuses(call, code):
    with pytest.raises(AgentflowError) as exc:
        call()
    assert exc.value.code is code
    return str(exc.value)


def test_it_implements_the_protocol(service):
    assert isinstance(service, WorkspaceService)


def test_status_and_next_without_a_task(service):
    status = service.status()
    assert status.active_task is None and status.workflow == "sample" and status.next
    assert service.next_step().kind == ActionKind.START_TASK


def test_status_follows_the_task_as_it_changes(service, repo):
    main(["task", "new", "A task"])
    task = service.status().active_task
    assert (task.id, task.current_step, task.step_status, task.max_rounds) == ("T-001", "confirm", "in_progress", 2)
    assert service.next_step().kind == ActionKind.CONTINUE
    main(["task", "advance", "--result", "pass"])
    assert service.next_step().kind == ActionKind.AWAIT_APPROVAL
    assert service.status().active_task.step_status == "awaiting_approval"


def test_report_write_is_the_same_as_the_cli_and_returns_the_path(service, repo):
    main(["task", "new", "t"])
    info = service.write_report("confirm", "# Confirmed\nall clear")
    assert info.path.endswith("confirm.md") and info.bytes == len("# Confirmed\nall clear\n")
    assert (repo / ".agentflow" / "tasks" / "T-001" / "reports" / "confirm.md").read_text(encoding="utf-8").startswith("# Confirmed")


def test_report_write_follows_the_rules_of_the_cli(service):
    refuses(lambda: service.write_report("confirm", "x"), ExitCode.NO_ACTIVE_TASK)
    main(["task", "new", "t"])
    refuses(lambda: service.write_report("ghost", "x"), ExitCode.UNKNOWN_STEP)
    refuses(lambda: service.write_report("confirm", "  "), ExitCode.INVALID_INPUT)
    assert "current step 'confirm'" in refuses(lambda: service.write_report("build", "x"), ExitCode.REPORT_REFUSED)
    service.write_report("confirm", "done")
    main(["task", "advance", "--result", "pass"])
    assert "final" in refuses(lambda: service.write_report("confirm", "changed my mind"), ExitCode.REPORT_REFUSED)


def test_plan_check_reports_problems_as_a_result(service):
    refuses(service.plan_check, ExitCode.NO_ACTIVE_TASK)
    main(["task", "new", "t"])
    main(["task", "advance", "--result", "pass"])
    main(["task", "approve"])  # now at "build", the plan step
    refuses(service.plan_check, ExitCode.PLAN_INVALID)  # no plan report yet
    service.write_report("build", "### C1 - x\n- role: nobody\n")
    result = service.plan_check()
    assert not result.ok and any("unknown role" in problem for problem in result.problems)
    service.write_report("build", GOOD_PLAN)
    assert service.plan_check().ok and service.plan_check().problems == ()


def test_scan_summary_without_results(service):
    assert service.scan_summary().tools == ()
    main(["task", "new", "t"])
    summary = service.scan_summary()
    assert summary.task == "T-001" and summary.tools == () and summary.blocking == ()


# ------------------------------------------------------------ project documents


def test_project_write_stores_the_section(service, repo):
    info = service.write_project(ProjectSection.PROFILE, "# Profile\r\nA web shop\r\n")
    path = repo / ".agentflow" / "project" / "profile.md"
    assert info.path == str(path) and path.read_bytes() == b"# Profile\nA web shop\n"
    service.write_project(ProjectSection.PROFILE, "# Profile v2")
    assert path.read_text(encoding="utf-8") == "# Profile v2\n"


def test_project_write_rejects_empty_content_and_unknown_sections(service):
    refuses(lambda: service.write_project(ProjectSection.SOURCES, " \n"), ExitCode.INVALID_INPUT)
    with pytest.raises(ValueError):
        ProjectSection("secrets")


def test_project_documents_are_not_written_while_a_task_is_open(service, repo):
    main(["task", "new", "t"])
    message = refuses(lambda: service.write_project(ProjectSection.PROFILE, "# P"), ExitCode.PROJECT_WRITE_REFUSED)
    assert "task" in message and not (repo / ".agentflow" / "project" / "profile.md").exists()
    main(["task", "cancel"])
    service.write_project(ProjectSection.PROFILE, "# P")


# ------------------------------------------------------------------- knowledge


@pytest.fixture
def knowledge(repo):
    root = repo / ".agentflow" / "knowledge"
    (root / "lessons").mkdir(parents=True, exist_ok=True)
    (root / "lessons" / "retries.md").write_text("# Retries\nAlways back off.\nNever retry a POST.\n", encoding="utf-8")
    (root / "conventions.md").write_text("Prefer Enums over strings.\n", encoding="utf-8")
    (root / "image.png").write_bytes(b"\x89PNG not text")
    return root


def test_knowledge_search_finds_lines_case_insensitively(service, knowledge):
    hits = service.knowledge_search("RETRY", 10)
    assert [(hit.file, hit.line) for hit in hits] == [("lessons/retries.md", 3)]
    assert "Never retry" in hits[0].text
    assert service.knowledge_search("enums", 10)[0].file == "conventions.md"
    assert service.knowledge_search("nothing like this", 10) == []


def test_knowledge_search_limits_and_ignores_empty_queries(service, knowledge):
    assert len(service.knowledge_search("e", 1)) == 1
    refuses(lambda: service.knowledge_search("  ", 5), ExitCode.INVALID_INPUT)
    assert not [hit for hit in service.knowledge_search("png", 10)]  # binary files are not searched


def test_knowledge_read_returns_a_file_inside_the_workspace_copy(service, knowledge):
    assert service.knowledge_read("lessons/retries.md").content.startswith("# Retries")
    assert service.knowledge_read("conventions.md").file == "conventions.md"


@pytest.mark.parametrize("name", ["../config.yaml", "..\\config.yaml", "/etc/hosts", "C:/Windows/win.ini", "lessons/../../state.json", "missing.md", "lessons", "image.png"])
def test_knowledge_read_stays_inside_the_knowledge_folder(service, knowledge, name):
    with pytest.raises(AgentflowError) as exc:
        service.knowledge_read(name)
    assert exc.value.code in {ExitCode.KNOWLEDGE_NOT_FOUND, ExitCode.INVALID_INPUT}
