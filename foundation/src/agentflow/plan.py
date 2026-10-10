"""The plan a planner writes, and the checks that make it fit to build from.

A plan is Markdown. Each checklist item is a heading ``### C1 - <title>`` followed by bullets
``- role: ...``, ``- files: ...``, ``- done-when: ...`` and ``- docs: ...``.
"""

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from agentflow.constants import PLAN_ITEM_CODE_PATTERN, PLAN_NO_DOCS_PREFIX, PLAN_NO_FILES_PREFIX, PlanField
from agentflow.interfaces import PlanRule, RoleRegistry

_HEADING = re.compile(rf"^###\s+({PLAN_ITEM_CODE_PATTERN})\b\s*(?:[—–:-]+\s*)?(.*?)\s*$")
_BAD_HEADING = re.compile(r"^###\s+(\S+)")
_FIELD = re.compile(r"^\s*[-*]\s+([A-Za-z-]+)\s*:\s*(.*?)\s*$")
_FIELD_NAMES = {field.value: field for field in PlanField}
_URL = re.compile(r"https?://\S+")
_REASON_SEPARATOR = re.compile(r"^\s*[—–:-]+\s*(.+)$")
_FILE_SEPARATOR = re.compile(r"\s*,\s*")
_BACKTICKS = "`"
_CODE_FENCE = "```"


@dataclass(frozen=True)
class PlanItem:
    code: str
    title: str
    role: str | None = None
    # ``None`` when the item has no files line at all; empty tuple for "không có".
    files: tuple[str, ...] | None = None
    done_when: str | None = None
    # Raw docs value: URLs, or "không có — <reason>".
    docs: str | None = None

    @property
    def docs_links(self) -> tuple[str, ...]:
        return tuple(_URL.findall(self.docs or ""))


@dataclass(frozen=True)
class Plan:
    items: tuple[PlanItem, ...]
    # Headings that start with ``###`` but are not a valid item code, kept to report them.
    bad_headings: tuple[str, ...] = ()


@dataclass(frozen=True)
class PlanProblem:
    message: str
    code: str | None = None

    def __str__(self) -> str:
        return f"{self.code}: {self.message}" if self.code else self.message


def parse_plan(text: str) -> Plan:
    items: list[PlanItem] = []
    bad: list[str] = []
    current: dict[str, object] | None = None
    in_fence = False

    def close() -> None:
        if current is not None:
            items.append(PlanItem(**current))  # type: ignore[arg-type]

    for line in text.replace("\r\n", "\n").split("\n"):
        if line.strip().startswith(_CODE_FENCE):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        heading = _HEADING.match(line)
        if heading:
            close()
            current = {"code": heading.group(1), "title": heading.group(2)}
            continue
        loose = _BAD_HEADING.match(line)
        if loose:
            close()
            current = None
            bad.append(loose.group(1))
            continue
        field = _FIELD.match(line)
        if current is not None and field and field.group(1).lower() in _FIELD_NAMES:
            _store(current, _FIELD_NAMES[field.group(1).lower()], field.group(2))
    close()
    return Plan(tuple(items), tuple(bad))


def _store(current: dict[str, object], field: PlanField, value: str) -> None:
    match field:
        case PlanField.ROLE:
            current["role"] = value.strip(_BACKTICKS).strip()
        case PlanField.FILES:
            current["files"] = _parse_files(value)
        case PlanField.DONE_WHEN:
            current["done_when"] = value
        case PlanField.DOCS:
            current["docs"] = value


def _parse_files(value: str) -> tuple[str, ...]:
    if value.lower().startswith(PLAN_NO_FILES_PREFIX):
        return ()
    parts = (part.strip().strip(_BACKTICKS).strip() for part in _FILE_SEPARATOR.split(value))
    return tuple(part for part in parts if part)


def docs_problem(docs: str | None) -> str | None:
    if docs is None or not docs.strip():
        return f"missing '{PlanField.DOCS}' (give a link, or '{PLAN_NO_DOCS_PREFIX} — <reason>')"
    if _URL.search(docs):
        return None
    if docs.lower().startswith(PLAN_NO_DOCS_PREFIX):
        reason = _REASON_SEPARATOR.match(docs[len(PLAN_NO_DOCS_PREFIX) :])
        if reason and reason.group(1).strip():
            return None
        return f"'{PlanField.DOCS}: {PLAN_NO_DOCS_PREFIX}' needs a reason after it"
    return f"'{PlanField.DOCS}' must be a link (http/https) or '{PLAN_NO_DOCS_PREFIX} — <reason>'"


def check_plan(
    plan: Plan,
    roles: RoleRegistry,
    rules: Sequence[PlanRule] = (),
    require_files: bool = False,
) -> list[PlanProblem]:
    """Every problem found, so the planner can fix them in one go."""
    problems: list[PlanProblem] = [PlanProblem(f"heading '### {name}' is not a valid item code (C1, C2, ...)") for name in plan.bad_headings]
    if not plan.items:
        problems.append(PlanProblem("the plan has no checklist items (### C1 - <title>)"))
    seen: set[str] = set()
    valid_roles = roles.roles()
    for item in plan.items:
        if item.code in seen:
            problems.append(PlanProblem("duplicate item code", item.code))
        seen.add(item.code)
        problems += _item_problems(item, valid_roles, require_files)
        for rule in rules:
            problems += (PlanProblem(message, item.code) for message in rule.problems(item))
    return problems


def _item_problems(item: PlanItem, valid_roles: Iterable[str], require_files: bool) -> list[PlanProblem]:
    found: list[PlanProblem] = []
    if not item.role:
        found.append(PlanProblem(f"missing '{PlanField.ROLE}'", item.code))
    elif item.role not in valid_roles:
        found.append(PlanProblem(f"unknown role '{item.role}' (valid: {', '.join(sorted(valid_roles))})", item.code))
    if not item.done_when or not item.done_when.strip():
        found.append(PlanProblem(f"missing '{PlanField.DONE_WHEN}'", item.code))
    if (message := docs_problem(item.docs)) is not None:
        found.append(PlanProblem(message, item.code))
    if require_files and item.files is None:
        found.append(PlanProblem(f"missing '{PlanField.FILES}' (list the paths this item changes, or '{PLAN_NO_FILES_PREFIX}')", item.code))
    return found
