"""The task summary a person reads before (and after) approving the last step."""

from collections.abc import Sequence

from agentflow.models import CommitInfo, Task
from agentflow.plan import PlanItem

SHORT_SHA = 9
NO_ITEM_GROUP = "other commits"
NONE_LINE = "- none"


def build_summary(
    task: Task,
    items: Sequence[PlanItem],
    commits: Sequence[CommitInfo],
    scan_lines: Sequence[str],
    approver: str,
    approved_at: str,
) -> str:
    lines = [
        f"# {task.id}: {task.title}",
        "",
        f"- Branch: {task.branch}",
        f"- Approved by: {approver}",
        f"- Approved at: {approved_at}",
        "",
        "## Plan items",
        "",
    ]
    by_item: dict[str | None, list[CommitInfo]] = {}
    for commit in commits:
        by_item.setdefault(commit.item, []).append(commit)
    for item in items:
        lines += [f"### {item.code} - {item.title}", ""]
        lines += [f"- Role: {item.role or '?'}", f"- Done when: {item.done_when or '?'}"]
        links = item.docs_links
        lines.append(f"- Docs: {', '.join(links) if links else (item.docs or 'none')}")
        lines += ["- Commits:", *_commit_lines(by_item.pop(item.code, []), indent="  ")]
        lines.append("")
    leftover = [commit for group in by_item.values() for commit in group]
    if leftover or not items:
        lines += [f"### {NO_ITEM_GROUP}", "", *_commit_lines(leftover), ""]
    lines += ["## Scans", ""]
    lines += [f"- {line}" for line in scan_lines] or [NONE_LINE]
    return "\n".join(lines) + "\n"


def _commit_lines(commits: Sequence[CommitInfo], indent: str = "") -> list[str]:
    if not commits:
        return [f"{indent}{NONE_LINE}"]
    return [f"{indent}- {commit.sha[:SHORT_SHA]} {commit.subject}" for commit in commits]
