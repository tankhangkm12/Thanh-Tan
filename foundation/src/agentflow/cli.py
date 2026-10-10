"""Command-line entry point for agentflow."""

import argparse
import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import version
from pathlib import Path

from agentflow.constants import (
    CONTAINER_TOOLS,
    ENCODING,
    EXCLUDE_ENTRY,
    IN_FLIGHT_TASK_STATUSES,
    PACKAGE_NAME,
    STEP_RESULTS,
    VERSION_FLAG,
    WORKSPACE_DIR,
    CliKind,
    Command,
    DriftStatus,
    GateKind,
    PlanCommand,
    ExitCode,
    HookEvent,
    SyncOutcome,
    TaskCommand,
    TaskEvent,
    TaskType,
    ToolStatus,
    WorkflowCommand,
)
from agentflow.commit import commit_staged
from agentflow.doctor import SystemToolProbe, run_doctor
from agentflow.engine import next_action
from agentflow.errors import AgentflowError
from agentflow.gates import GateContext, WorkspaceGates, plan_problems, plan_report_path
from agentflow.git import GitBranchLookup, SubprocessGit
from agentflow.guard import evaluate, parse_request, verdict_to_dict
from agentflow.hook import handle_hook
from agentflow.models import State, ToolCheck, Workflow
from agentflow.plan import parse_plan
from agentflow.projectcontext import load_project_context
from agentflow.render import NONE_TEXT, describe_action, describe_step
from agentflow.seal import TaskSealer
from agentflow.runner import SubprocessRunner
from agentflow.scanner import ContainerGitleaksScanner
from agentflow.state import JsonStateStore, utc_now
from agentflow.sync import sync_workflow, workflow_drift
from agentflow.tasks import (
    advance_task,
    approve_task,
    cancel_task,
    seal_finished_task,
    new_task,
    require_active_task,
    write_report,
)
from agentflow.workspace import (
    WorkspacePaths,
    find_workspace,
    init_workspace,
    load_config,
    load_workspace_workflow,
    GitWorkspaceLookup,
)

CLI_OPTION = "--cli"
TYPE_OPTION = "--type"
RESULT_OPTION = "--result"
REASON_OPTION = "--reason"
STEP_OPTION = "--step"
SHORT_SHA_LENGTH = 9
WORKFLOW_OPTION = "--workflow"
FILE_OPTION = "--file"
COMMIT_OPTION = "--commit"
ITEM_OPTION = "--item"
FORCE_OPTION = "--force"
ERROR_PREFIX = "error: "
WARNING_PREFIX = "warning: "
SYNC_HINT = "run `agentflow workflow sync` to use the new version"

Handler = Callable[[argparse.Namespace], ExitCode]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=PACKAGE_NAME, description="Shared engine for plugin family workflows.")
    parser.add_argument(VERSION_FLAG, action="version", version=f"{PACKAGE_NAME} {version(PACKAGE_NAME)}")
    commands = parser.add_subparsers(dest="command", metavar="<command>")

    commands.add_parser(Command.DOCTOR, help="check uv, git and a container runtime")

    init = commands.add_parser(Command.INIT, help=f"create or complete {EXCLUDE_ENTRY} in this git repository")
    init.add_argument(WORKFLOW_OPTION, required=True, type=Path, help="family workflow.yaml to copy in")

    commands.add_parser(Command.STATUS, help="show the open task, its current step and what comes next")
    commands.add_parser(Command.NEXT, help="show the next step for the workflow and current state")

    workflow = commands.add_parser(Command.WORKFLOW, help="manage the workspace's workflow copy")
    workflow_commands = workflow.add_subparsers(dest="workflow_command", metavar="<workflow command>", required=True)
    sync = workflow_commands.add_parser(WorkflowCommand.SYNC, help="replace the copy with the checked source")
    sync.add_argument(FORCE_OPTION, action="store_true", help="sync even while tasks are mid-workflow")

    task = commands.add_parser(Command.TASK, help="start, advance, approve or cancel a task")
    task_commands = task.add_subparsers(dest="task_command", metavar="<task command>", required=True)
    new = task_commands.add_parser(TaskCommand.NEW, help="create the task's gitflow branch and record the task")
    new.add_argument("title", help="what the task is about")
    new.add_argument(TYPE_OPTION, type=TaskType, choices=list(TaskType), default=TaskType.FEATURE)
    advance = task_commands.add_parser(TaskCommand.ADVANCE, help="record that the current step passed or failed")
    advance.add_argument(RESULT_OPTION, required=True, type=TaskEvent, choices=list(STEP_RESULTS))
    approve = task_commands.add_parser(TaskCommand.APPROVE, help="approve the step, or resume a blocked task")
    approve.add_argument(REASON_OPTION, help="why a blocked task is resumed (kept in decisions/)")
    task_commands.add_parser(TaskCommand.CANCEL, help="cancel the active task")
    seal = task_commands.add_parser(TaskCommand.SEAL, help="for a person: write summary.md and the approval tag of a finished task")
    seal.add_argument("task_id", help="id of a finished task, e.g. T-001")
    seal.add_argument(COMMIT_OPTION, help="tag this commit instead of the task branch's tip (e.g. after the branch was deleted)")

    plan = commands.add_parser(Command.PLAN, help="check the plan of the active task")
    plan_commands = plan.add_subparsers(dest="plan_command", metavar="<plan command>", required=True)
    check = plan_commands.add_parser(PlanCommand.CHECK, help="every item needs a code, a valid role, done-when and docs")
    check.add_argument(FILE_OPTION, type=Path, help="check this Markdown file instead of the task's plan report")

    report = commands.add_parser(Command.REPORT, help="store a step report read from stdin")
    report.add_argument(STEP_OPTION, required=True, help="step id the report belongs to")

    commit = commands.add_parser(Command.COMMIT, help="scan staged changes for secrets, then commit with the task prefix")
    commit.add_argument("message", help="commit message, without the task prefix")
    commit.add_argument(ITEM_OPTION, help="plan item (C1, ...) this commit belongs to")

    commands.add_parser(Command.GUARD, help='read {"command", "cwd"} JSON from stdin, print an allow/deny verdict')

    hook = commands.add_parser(Command.HOOK, help="answer a Claude Code or Antigravity hook (JSON on stdin)")
    hook.add_argument("event", type=HookEvent, choices=list(HookEvent))
    hook.add_argument(CLI_OPTION, required=True, type=CliKind, choices=list(CliKind))
    return parser


def main(argv: list[str] | None = None) -> int:
    _utf8_when_redirected()
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return ExitCode.USAGE
    try:
        return handler(args)
    except AgentflowError as exc:
        _err(f"{ERROR_PREFIX}{exc}")
        return exc.code


# ---------------------------------------------------------------- handlers


def cmd_doctor(args: argparse.Namespace) -> ExitCode:
    report = run_doctor(SystemToolProbe())
    width = max(len(check.tool) for check in report.checks)
    for check in report.checks:
        print(_doctor_line(check, width))
    if not any(c.status is not ToolStatus.MISSING for c in report.checks if c.tool in CONTAINER_TOOLS):
        print(f"container runtime: install at least one of {', '.join(CONTAINER_TOOLS)}")
    if report.ok:
        print("result: all required tools found")
        return ExitCode.OK
    print("result: required tools are missing")
    return ExitCode.MISSING_REQUIREMENT


def _doctor_line(check: ToolCheck, width: int) -> str:
    label = f"[{check.status}]".ljust(len(f"[{ToolStatus.WARNING}]"))
    parts = [part for part in (check.version, check.detail) if part]
    if check.status is ToolStatus.MISSING:
        parts.append(f"install: {check.install_url}")
    return f"{label} {check.tool.ljust(width)}  {'; '.join(parts)}"


def cmd_init(args: argparse.Namespace) -> ExitCode:
    result = init_workspace(Path.cwd(), args.workflow)
    paths = result.paths
    config = load_config(paths)
    print(f"workspace: {paths.dir}")
    print(f"created: {', '.join(result.created)}" if result.created else "created: nothing, workspace was complete")
    copy_note = "copied" if result.workflow_copied else "kept the existing copy"
    print(f"workflow: {config.workflow.family} ({copy_note}; source {config.workflow.source_path})")
    print(f"git exclude: added {EXCLUDE_ENTRY}" if result.exclude_added else "git exclude: already excluded")
    _warn_drift(workflow_drift(config))
    return ExitCode.OK


@dataclass(frozen=True)
class _Opened:
    paths: WorkspacePaths
    workflow: Workflow
    state: State


def _open_workspace() -> _Opened:
    """Workspace, workflow copy in use and validated state; warns when the source drifted."""
    paths = find_workspace(Path.cwd())
    config = load_config(paths)
    workflow = load_workspace_workflow(paths)
    state = JsonStateStore(paths.dir, workflow).load()
    _warn_drift(workflow_drift(config))
    return _Opened(paths, workflow, state)


def cmd_status(args: argparse.Namespace) -> ExitCode:
    opened = _open_workspace()
    workflow, state = opened.workflow, opened.state
    task = state.active_task()
    print(f"workspace: {opened.paths.dir}")
    print(f"workflow: {workflow.family} ({len(workflow.steps)} steps)")
    print(f"active task: {NONE_TEXT if task is None else f'{task.id} {task.title}'}")
    if task is not None:
        step = workflow.get_step(task.current_step)
        step_text = describe_step(step) if step else task.current_step
        print(f"current step: {step_text}, {task.step_status}")
        rounds = f"{task.loop_round}/{workflow.max_rounds}"
        print(f"task status: {task.status}; rework rounds: {rounds}; branch: {task.branch or NONE_TEXT}")
    others = [t for t in state.tasks if t.status in IN_FLIGHT_TASK_STATUSES and t is not task]
    if others:
        print("other open tasks: " + ", ".join(f"{t.id} ({t.current_step}, {t.status})" for t in others))
    print(f"next: {describe_action(next_action(workflow, task))}")
    return ExitCode.OK


def cmd_next(args: argparse.Namespace) -> ExitCode:
    opened = _open_workspace()
    action = next_action(opened.workflow, opened.state.active_task())
    print(f"{action.kind}: {describe_action(action)}")
    return ExitCode.OK


def cmd_workflow(args: argparse.Namespace) -> ExitCode:
    # argparse requires a workflow subcommand, and sync is the only one so far.
    result = sync_workflow(Path.cwd(), force=args.force)
    if result.outcome is SyncOutcome.UNCHANGED:
        print("workflow: already in sync with its source")
        return ExitCode.OK
    print("workflow: copy replaced with the source version")
    if result.forced_task_ids:
        _err(f"{WARNING_PREFIX}synced with --force while tasks were open: {', '.join(result.forced_task_ids)}")
    return ExitCode.OK


def _store(opened: _Opened) -> JsonStateStore:
    return JsonStateStore(opened.paths.dir, opened.workflow)


def cmd_task(args: argparse.Namespace) -> ExitCode:
    opened = _open_workspace()
    store = _store(opened)
    match args.task_command:
        case TaskCommand.NEW:
            task = new_task(store, opened.workflow, SubprocessGit(opened.paths.root), args.title, args.type, utc_now)
            print(f"{task.id} created on branch {task.branch}")
        case TaskCommand.ADVANCE:
            task = advance_task(store, opened.workflow, args.result, utc_now, _gates(opened), _sealer(opened))
            print(f"{task.id}: step '{task.current_step}' is now {task.step_status} (task {task.status})")
        case TaskCommand.APPROVE:
            result = approve_task(store, opened.workflow, opened.paths.dir, utc_now, args.reason, _sealer(opened))
            task = result.task
            print(f"{task.id}: step '{task.current_step}' is now {task.step_status} (task {task.status})")
            if result.decision_file is not None:
                print(f"decision recorded: {result.decision_file}")
        case TaskCommand.CANCEL:
            task = cancel_task(store, opened.workflow, utc_now)
            print(f"{task.id} cancelled")
        case TaskCommand.SEAL:
            path = seal_finished_task(store, _sealer(opened), args.task_id, args.commit)
            print(f"{args.task_id} sealed; summary: {path}")
    state = store.load()
    print(f"next: {describe_action(next_action(opened.workflow, state.active_task()))}")
    return ExitCode.OK


def _sealer(opened: _Opened) -> TaskSealer:
    return TaskSealer(SubprocessGit(opened.paths.root), opened.paths.dir, opened.workflow, utc_now)


def _plan_item_codes(opened: _Opened) -> set[str] | None:
    """Item codes of the active task's plan, or ``None`` while there is no plan report."""
    task = opened.state.active_task()
    step = next((s for s in opened.workflow.steps if GateKind.PLAN_VALID in s.gates), None)
    if task is None or step is None:
        return None
    path = plan_report_path(opened.paths.dir, task.id, step.id)
    if not path.is_file():
        return None
    return {item.code for item in parse_plan(path.read_text(encoding=ENCODING)).items}


def _gates(opened: _Opened) -> WorkspaceGates:
    project = load_project_context(opened.paths.dir, opened.workflow)
    return WorkspaceGates(GateContext(opened.paths.dir, opened.workflow, project))


def cmd_plan(args: argparse.Namespace) -> ExitCode:
    # argparse requires a plan subcommand, and check is the only one so far.
    opened = _open_workspace()
    project = load_project_context(opened.paths.dir, opened.workflow)
    if args.file is not None:
        text = args.file.read_text(encoding=ENCODING)
    else:
        task = require_active_task(opened.state)
        step = next((s for s in opened.workflow.steps if GateKind.PLAN_VALID in s.gates), None)
        if step is None:
            raise AgentflowError("the workflow has no step that checks a plan", ExitCode.INVALID_INPUT)
        path = plan_report_path(opened.paths.dir, task.id, step.id)
        if not path.is_file():
            raise AgentflowError(f"no plan report yet: {path}", ExitCode.PLAN_INVALID)
        text = path.read_text(encoding=ENCODING)
    problems = plan_problems(text, project)
    if problems:
        for problem in problems:
            print(f"- {problem}")
        raise AgentflowError(f"the plan has {len(problems)} problem(s)", ExitCode.PLAN_INVALID)
    print("plan ok")
    return ExitCode.OK


def cmd_report(args: argparse.Namespace) -> ExitCode:
    opened = _open_workspace()
    task = require_active_task(opened.state)
    path = write_report(opened.paths.dir, opened.workflow, task, args.step, sys.stdin.read())
    print(f"report saved: {path}")
    return ExitCode.OK


def cmd_commit(args: argparse.Namespace) -> ExitCode:
    opened = _open_workspace()
    scanner = ContainerGitleaksScanner(SubprocessRunner())
    result = commit_staged(
        _store(opened), SubprocessGit(opened.paths.root), scanner, args.message, args.item, _plan_item_codes(opened)
    )
    print(f"committed {result.sha[:SHORT_SHA_LENGTH]}: {result.message}")
    return ExitCode.OK


def cmd_guard(args: argparse.Namespace) -> ExitCode:
    request = parse_request(sys.stdin.read())
    verdict = evaluate(request.command, request.cwd or Path.cwd(), GitBranchLookup(), GitWorkspaceLookup())
    print(json.dumps(verdict_to_dict(verdict), ensure_ascii=False))
    return ExitCode.OK


def cmd_hook(args: argparse.Namespace) -> ExitCode:
    # Hooks must not break the agent: report problems on stderr but always exit 0.
    try:
        output = handle_hook(args.event, args.cli, sys.stdin.read(), GitBranchLookup())
    except Exception as exc:  # noqa: BLE001 - a crashing hook would otherwise surface as a tool error
        _err(f"{WARNING_PREFIX}agentflow hook failed: {exc}")
        return ExitCode.OK
    if output:
        print(output)
    return ExitCode.OK


HANDLERS: dict[str, Handler] = {
    Command.HOOK: cmd_hook,
    Command.DOCTOR: cmd_doctor,
    Command.INIT: cmd_init,
    Command.STATUS: cmd_status,
    Command.NEXT: cmd_next,
    Command.WORKFLOW: cmd_workflow,
    Command.TASK: cmd_task,
    Command.PLAN: cmd_plan,
    Command.REPORT: cmd_report,
    Command.COMMIT: cmd_commit,
    Command.GUARD: cmd_guard,
}


# ----------------------------------------------------------------- helpers


def _warn_drift(drift: DriftStatus) -> None:
    if drift is DriftStatus.SOURCE_CHANGED:
        _err(f"{WARNING_PREFIX}the workflow source changed since it was copied; {SYNC_HINT}")
    elif drift is DriftStatus.SOURCE_MISSING:
        _err(f"{WARNING_PREFIX}the workflow source no longer exists; using the copy in {WORKSPACE_DIR}/")


def _err(message: str) -> None:
    print(message, file=sys.stderr)


def _utf8_when_redirected() -> None:
    # Workflow names are often non-ASCII; a redirected Windows stream defaults to a legacy code page.
    for stream in (sys.stdout, sys.stderr):
        if not stream.isatty() and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding=ENCODING)
