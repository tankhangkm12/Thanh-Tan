"""What the checks need to know about the project: valid roles, plan rules, scan tools, gates and settings.

The workflow supplies the base; registered extensions add to it.
"""

from collections.abc import Callable, Collection, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from agentflow.constants import CheckKind, GateKind, PlanRuleKind
from agentflow.convention_sources import load_effective_conventions
from agentflow.plan_rules import ItemOrderRule
from agentflow.ext_rules import ExtensionRules
from agentflow.extensions import load_registered
from agentflow.interfaces import PlanRule, PlanWideRule
from agentflow.models import Workflow
from agentflow.scan_types import ScanToolSpec
from agentflow.settings import get_value
from agentflow.workspace import WorkspacePaths, load_config


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
    # Added by extensions: scan tools, gates (step id, kind), a project-settings lookup and commit rules.
    scan_tools: tuple[ScanToolSpec, ...] = ()
    extra_gates: tuple[tuple[str, GateKind], ...] = ()
    # Checks on a whole plan that enforced conventions switch on (such as the order of interface and implement items).
    plan_wide_rules: tuple[PlanWideRule, ...] = ()
    lookup: Callable[[str], Any] = field(default=lambda key: None)
    rules: ExtensionRules | None = None


def load_project_context(workspace_dir: Path, workflow: Workflow) -> ProjectContext:
    paths = WorkspacePaths(workspace_dir.parent)
    roles = {step.role for step in workflow.steps}
    registered = load_registered(paths)
    wide = tuple(
        ItemOrderRule(item.convention.code)
        for item in load_effective_conventions(workspace_dir).checked_by(CheckKind.PLAN)
        if item.convention.rule == PlanRuleKind.ITEM_ORDER
    )
    if not registered:
        return ProjectContext(RoleSet(frozenset(roles)), plan_wide_rules=wide, require_files=bool(wide))
    settings = load_config(paths).settings
    extensions = [item.extension for item in registered]
    roles |= {role for extension in extensions for role in extension.role_ids}

    def lookup(key: str) -> Any:
        return get_value(settings, key)

    rules = ExtensionRules(extensions, lookup)
    return ProjectContext(
        roles=RoleSet(frozenset(roles)),
        plan_rules=(rules,),
        require_files=rules.requires_files or bool(wide),
        plan_wide_rules=wide,
        scan_tools=tuple(tool for extension in extensions for tool in extension.scan_tools),
        extra_gates=tuple(gate for extension in extensions for gate in extension.gates),
        lookup=lookup,
        rules=rules,
    )
