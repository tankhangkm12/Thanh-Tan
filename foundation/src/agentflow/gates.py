"""Gates: checks a step has to satisfy before it can pass. Foundation knows the kinds, workflows choose where they apply."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from agentflow.constants import ENCODING, MARKDOWN_SUFFIX, REPORTS_DIR, TASKS_DIR, GateKind
from agentflow.models import Step, Task, Workflow
from agentflow.plan import check_plan, parse_plan
from agentflow.projectcontext import ProjectContext


@dataclass(frozen=True)
class GateContext:
    workspace_dir: Path
    workflow: Workflow
    project: ProjectContext


GateCheck = Callable[[GateContext, Task, Step], list[str]]


def plan_report_path(workspace_dir: Path, task_id: str, step_id: str) -> Path:
    return workspace_dir / TASKS_DIR / task_id / REPORTS_DIR / f"{step_id}{MARKDOWN_SUFFIX}"


def plan_problems(text: str, project: ProjectContext) -> list[str]:
    plan = parse_plan(text)
    return [str(p) for p in check_plan(plan, project.roles, project.plan_rules, project.require_files)]


def _plan_valid(context: GateContext, task: Task, step: Step) -> list[str]:
    path = plan_report_path(context.workspace_dir, task.id, step.id)
    if not path.is_file():
        return [f"no plan report for step '{step.id}' yet (save it with `agentflow report --step {step.id}`)"]
    return plan_problems(path.read_text(encoding=ENCODING), context.project)


CHECKS: dict[GateKind, GateCheck] = {GateKind.PLAN_VALID: _plan_valid}


class WorkspaceGates:
    """``GateRunner`` for a real workspace. Gate kinds without a registered check are skipped."""

    def __init__(
        self,
        context: GateContext,
        extra: Callable[[Step], Sequence[GateKind]] = lambda step: (),
        checks: dict[GateKind, GateCheck] | None = None,
    ) -> None:
        self.context = context
        self.extra = extra
        self.checks = CHECKS if checks is None else checks

    def problems(self, task: Task, step: Step) -> list[str]:
        kinds = dict.fromkeys((*step.gates, *self.extra(step)))
        found: list[str] = []
        for kind in kinds:
            check = self.checks.get(kind)
            if check is not None:
                found += [f"[{kind}] {message}" for message in check(self.context, task, step)]
        return found
