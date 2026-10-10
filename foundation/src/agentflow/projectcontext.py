"""What the checks need to know about the project: valid roles and extra plan rules. Extensions add to it."""

from collections.abc import Collection, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from agentflow.interfaces import PlanRule
from agentflow.models import Workflow


@dataclass(frozen=True)
class RoleSet:
    names: frozenset[str]

    def roles(self) -> Collection[str]:
        return self.names


@dataclass(frozen=True)
class ProjectContext:
    roles: RoleSet
    plan_rules: Sequence[PlanRule] = field(default_factory=tuple)
    # True when some rule looks at the paths an item changes, so every item must list them.
    require_files: bool = False


def load_project_context(workspace_dir: Path, workflow: Workflow) -> ProjectContext:
    return ProjectContext(RoleSet(frozenset(step.role for step in workflow.steps)))
