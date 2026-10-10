"""Load a family's workflow file and check it: JSON Schema first, then cross-references."""

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from agentflow.constants import ENCODING, WORKFLOW_SCHEMA_FILE, ExitCode, StepKind
from agentflow.errors import AgentflowError
from agentflow.fsutil import file_sha256
from agentflow.models import Workflow, workflow_from_dict
from agentflow.validation import schema_errors

_INDENT = "\n  - "


def load_workflow(path: Path) -> Workflow:
    if not path.is_file():
        raise AgentflowError(f"workflow file not found: {path}", ExitCode.WORKFLOW_NOT_FOUND)
    try:
        data = yaml.safe_load(path.read_text(encoding=ENCODING))
    except (yaml.YAMLError, UnicodeDecodeError) as exc:
        raise AgentflowError(f"{path}: cannot read workflow: {exc}", ExitCode.INVALID_WORKFLOW) from exc
    return parse_workflow(data, origin=str(path))


def parse_workflow(data: Any, origin: str) -> Workflow:
    problems = schema_errors(data, WORKFLOW_SCHEMA_FILE)
    if not problems:
        workflow = workflow_from_dict(data)
        problems = reference_problems(workflow)
    if problems:
        raise AgentflowError(
            f"{origin}: invalid workflow:{_INDENT}{_INDENT.join(problems)}",
            ExitCode.INVALID_WORKFLOW,
        )
    return workflow


def reference_problems(workflow: Workflow) -> list[str]:
    """Rules JSON Schema cannot express: unique ids and valid step references."""
    problems: list[str] = []
    counts = Counter(step.id for step in workflow.steps)
    problems += [f"duplicate step id '{step_id}'" for step_id, n in counts.items() if n > 1]
    if not workflow.main_steps():
        problems.append(f"workflow needs at least one step of kind '{StepKind.STEP}'")

    position = {step.id: index for index, step in enumerate(workflow.steps)}
    for index, step in enumerate(workflow.steps):
        if step.on_fail is not None:
            target = workflow.get_step(step.on_fail)
            if target is None:
                problems.append(f"step '{step.id}': on_fail '{step.on_fail}' does not exist")
            elif target.kind is not StepKind.LOOP:
                problems.append(
                    f"step '{step.id}': on_fail '{step.on_fail}' must be a step of kind '{StepKind.LOOP}'"
                )
        if step.loop is not None:
            target = workflow.get_step(step.loop.back_to)
            if target is None:
                problems.append(f"step '{step.id}': back_to '{step.loop.back_to}' does not exist")
            elif target.kind is not StepKind.STEP:
                problems.append(
                    f"step '{step.id}': back_to '{step.loop.back_to}' must be a step of kind '{StepKind.STEP}'"
                )
            elif position[target.id] > index:
                problems.append(f"step '{step.id}': back_to '{step.loop.back_to}' must come before it")
    return problems


class FileWorkflowSource:
    """``WorkflowSource`` backed by a YAML file on disk."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> Workflow:
        return load_workflow(self.path)

    def fingerprint(self) -> str:
        return file_sha256(self.path)
