"""The three places conventions come from, and the list agents work to.

Highest priority first: decisions a person made (``decisions/*-answer-*.md``), the project's own
``project/conventions.md``, and the copy of the person's own conventions in ``knowledge/conventions.md``.
A convention replaces a lower one when it says ``overrides: <code>``; a lower source never replaces a higher one.
"""

from collections.abc import Iterator
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import yaml

from agentflow.constants import (
    CONVENTIONS_FILE,
    DECISION_ANSWER_INFIX,
    DECISION_ANSWER_KIND,
    DECISION_SCOPE_PROJECT,
    DECISIONS_DIR,
    ENCODING,
    KNOWLEDGE_DIR,
    MARKDOWN_SUFFIX,
    PROJECT_DIR,
    CheckKind,
    ConventionPrefix,
    ConventionSource,
    ConventionStatus,
    ExitCode,
)
from agentflow.conventions import Convention, ConventionDoc, parse_conventions, validate_conventions
from agentflow.errors import AgentflowError
from agentflow.fsutil import write_text_atomic

FRONTMATTER_FENCE = "---"
_RANK = {ConventionSource.DECISION: 0, ConventionSource.PROJECT: 1, ConventionSource.PERSONAL: 2}


@dataclass(frozen=True)
class SourcedConvention:
    convention: Convention
    source: ConventionSource


@dataclass(frozen=True)
class EffectiveConventions:
    items: tuple[SourcedConvention, ...] = ()
    problems: tuple[str, ...] = ()

    @property
    def enforced(self) -> tuple[SourcedConvention, ...]:
        """What is checked: everything a person made or confirmed. Unconfirmed project conventions are suggestions."""
        return tuple(item for item in self.items if item.convention.status is ConventionStatus.CONFIRMED)

    def checked_by(self, kind: CheckKind) -> tuple[SourcedConvention, ...]:
        return tuple(item for item in self.enforced if item.convention.check is kind)


# ------------------------------------------------------------- decisions


def answer_file_name(scope: str, question: str) -> str:
    return f"{scope}-{DECISION_ANSWER_INFIX}-{question}{MARKDOWN_SUFFIX}"


def _answer_files(workspace_dir: Path) -> Iterator[Path]:
    directory = workspace_dir / DECISIONS_DIR
    if directory.is_dir():
        yield from sorted(directory.glob(f"*-{DECISION_ANSWER_INFIX}-*{MARKDOWN_SUFFIX}"))


def _header_and_body(text: str) -> tuple[dict[str, Any], str] | None:
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != FRONTMATTER_FENCE or FRONTMATTER_FENCE not in lines[1:]:
        return None
    end = lines.index(FRONTMATTER_FENCE, 1)
    try:
        header = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None
    return (header, "\n".join(lines[end + 1 :]).strip()) if isinstance(header, dict) else None


def _read_answer(path: Path) -> Convention | str:
    """The convention a decision file holds, or the reason it cannot be read."""
    parts = _header_and_body(path.read_text(encoding=ENCODING))
    if parts is None or parts[0].get("kind") != DECISION_ANSWER_KIND:
        return f"{path.name}: not a convention answer (frontmatter with kind: {DECISION_ANSWER_KIND} is missing)"
    header, body = parts
    try:
        check = CheckKind(str(header.get("check")))
    except ValueError:
        return f"{path.name}: check '{header.get('check')}' is not one of: {', '.join(CheckKind)}"
    convention = Convention(
        code=str(header.get("code")),
        title=f"{header.get('question')} ({header.get('scope')})",
        check=check,
        rule=str(header["rule"]) if header.get("rule") else None,
        status=ConventionStatus.CONFIRMED,
        source=f"decision {path.name}",
        description=body or None,
        overrides=str(header["overrides"]) if header.get("overrides") else None,
    )
    problems = validate_conventions(ConventionDoc((convention,), prefix=ConventionPrefix.DECISION))
    return "; ".join(problems) if problems else convention


def load_decision_conventions(workspace_dir: Path) -> list[Convention]:
    return [item for item in map(_read_answer, _answer_files(workspace_dir)) if isinstance(item, Convention)]


def next_code(workspace_dir: Path) -> str:
    numbers = [int(c.code.split("-")[1]) for c in load_decision_conventions(workspace_dir)]
    return f"{ConventionPrefix.DECISION}-{max(numbers, default=0) + 1:02d}"


def write_answer(
    workspace_dir: Path,
    scope: str,
    question: str,
    code: str,
    text: str,
    check: CheckKind,
    rule: str | None,
    overrides: str | None,
    at: str,
) -> Path:
    """Record a person's answer to a question as a convention. One answer per question."""
    path = workspace_dir / DECISIONS_DIR / answer_file_name(scope, question)
    if path.exists():
        raise AgentflowError(f"{question} of {scope} is already answered ({path.name})", ExitCode.INVALID_INPUT)
    if not text.strip():
        raise AgentflowError("an answer needs text (--text)", ExitCode.INVALID_INPUT)
    header = {
        "kind": DECISION_ANSWER_KIND, "scope": scope, "question": question, "code": code, "check": str(check),
        "rule": rule, "overrides": overrides, "decided_at": at,
    }  # fmt: skip
    header = {key: value for key, value in header.items() if value is not None}
    body = f"{FRONTMATTER_FENCE}\n{yaml.safe_dump(header, sort_keys=False, allow_unicode=True)}{FRONTMATTER_FENCE}\n{text.strip()}\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    write_text_atomic(path, body)
    checked = _read_answer(path)
    if not isinstance(checked, Convention):
        path.unlink()
        raise AgentflowError(f"the answer is not a valid convention: {checked}", ExitCode.CONVENTIONS_INVALID)
    return path


# -------------------------------------------------------------- merging


def _doc(path: Path, prefix: str, label: str, problems: list[str]) -> ConventionDoc:
    if not path.is_file():
        return ConventionDoc(prefix=prefix)
    doc = parse_conventions(path.read_text(encoding=ENCODING), prefix)
    problems += [f"{label}: {problem}" for problem in validate_conventions(doc)]
    return doc


def load_effective_conventions(workspace_dir: Path) -> EffectiveConventions:
    problems: list[str] = []
    sourced: list[SourcedConvention] = []
    for path in _answer_files(workspace_dir):
        item = _read_answer(path)
        if isinstance(item, Convention):
            sourced.append(SourcedConvention(item, ConventionSource.DECISION))
        else:
            problems.append(item)
    project = _doc(workspace_dir / PROJECT_DIR / CONVENTIONS_FILE, ConventionPrefix.PROJECT, f"{PROJECT_DIR}/{CONVENTIONS_FILE}", problems)
    sourced += [SourcedConvention(item, ConventionSource.PROJECT) for item in project.conventions]
    personal = _doc(workspace_dir / KNOWLEDGE_DIR / CONVENTIONS_FILE, ConventionPrefix.PERSONAL, f"{KNOWLEDGE_DIR}/{CONVENTIONS_FILE}", problems)
    # What a person keeps in their own store needs no confirming.
    sourced += [
        SourcedConvention(replace(item, status=ConventionStatus.CONFIRMED), ConventionSource.PERSONAL) for item in personal.conventions
    ]
    sourced.sort(key=lambda item: _RANK[item.source])  # stable: file order is kept inside a source
    replaced: set[str] = set()
    by_code = {item.convention.code: item for item in sourced}
    for item in sourced:
        target = item.convention.overrides
        if not target:
            continue
        other = by_code.get(target)
        if other is None:
            problems.append(f"{item.convention.code}: overrides {target}, which does not exist")
        elif _RANK[item.source] < _RANK[other.source]:
            replaced.add(target)
        else:
            problems.append(f"{item.convention.code} cannot override {target}: it comes from a source of equal or lower priority")
    return EffectiveConventions(tuple(item for item in sourced if item.convention.code not in replaced), tuple(problems))
