"""Command-line entry point for agentflow."""

import argparse
import sys
from collections.abc import Callable
from importlib.metadata import version
from pathlib import Path

from agentflow.constants import (
    CONTAINER_TOOLS,
    ENCODING,
    EXCLUDE_ENTRY,
    PACKAGE_NAME,
    VERSION_FLAG,
    WORKSPACE_DIR,
    Command,
    DriftStatus,
    ExitCode,
    ToolStatus,
)
from agentflow.doctor import SystemToolProbe, run_doctor
from agentflow.errors import AgentflowError
from agentflow.models import ToolCheck
from agentflow.sync import workflow_drift
from agentflow.workspace import init_workspace, load_config

WORKFLOW_OPTION = "--workflow"
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


HANDLERS: dict[str, Handler] = {
    Command.DOCTOR: cmd_doctor,
    Command.INIT: cmd_init,
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
