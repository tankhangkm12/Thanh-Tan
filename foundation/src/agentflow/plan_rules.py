"""Plan rules that conventions switch on (``check: plan``)."""

from collections.abc import Sequence
from typing import Any

from agentflow.constants import PlanItemKind


class ItemOrderRule:
    """Interfaces before implementations: an ``implement`` item may not come before an ``interface`` item of the same file.

    While the rule is on, every item says what it is (``kind:``), and interface and implement items list their files.
    """

    def __init__(self, convention_code: str) -> None:
        self.code = convention_code

    def problems(self, items: Sequence[Any]) -> list[tuple[str | None, str]]:
        found: list[tuple[str | None, str]] = []
        for item in items:
            if item.kind is None:
                found.append((item.code, f"missing 'kind' ({', '.join(PlanItemKind)}), which {self.code} needs"))
            elif item.kind in {PlanItemKind.INTERFACE, PlanItemKind.IMPLEMENT} and item.files is None:
                found.append((item.code, f"missing 'files': {self.code} orders {item.kind} items by the files they touch"))
        for index, item in enumerate(items):
            if item.kind != PlanItemKind.IMPLEMENT:
                continue
            for later in items[index + 1 :]:
                shared = sorted(set(item.files or ()) & set(later.files or ()))
                if later.kind == PlanItemKind.INTERFACE and shared:
                    found.append(
                        (item.code, f"implements {', '.join(shared)} before its interface item {later.code} ({self.code}): put {later.code} first")
                    )
        return found
