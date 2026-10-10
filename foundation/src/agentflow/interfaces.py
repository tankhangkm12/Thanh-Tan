"""Contracts between agentflow parts, and between agentflow and plugin families.

A plugin family talks to agentflow only through a workflow file that a
``WorkflowSource`` loads; agentflow never imports family code.
"""

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from agentflow.models import ProbeResult, State, Workflow


@runtime_checkable
class WorkflowSource(Protocol):
    """Supplies a family's validated workflow and a fingerprint of its raw content."""

    def load(self) -> Workflow: ...

    def fingerprint(self) -> str:
        """sha256 hex digest of the raw workflow bytes."""
        ...


@runtime_checkable
class StateStore(Protocol):
    """Reads and writes the workspace state; ``save`` also regenerates STATE.md."""

    def load(self) -> State: ...

    def save(self, state: State) -> State:
        """Persist ``state`` and return it as written (with ``updated_at`` stamped)."""
        ...


@runtime_checkable
class ToolProbe(Protocol):
    """Looks up and runs external tools, so doctor can be tested without them."""

    def which(self, name: str) -> str | None: ...

    def run(self, args: Sequence[str]) -> ProbeResult: ...
