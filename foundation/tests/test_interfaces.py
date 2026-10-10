from collections.abc import Sequence

from agentflow.interfaces import StateStore, ToolProbe, WorkflowSource
from agentflow.models import ProbeResult, State, Workflow, workflow_from_dict


class FakeWorkflowSource:
    def __init__(self, workflow: Workflow) -> None:
        self._workflow = workflow

    def load(self) -> Workflow:
        return self._workflow

    def fingerprint(self) -> str:
        return "0" * 64


class FakeStateStore:
    def __init__(self) -> None:
        self.state = State()

    def load(self) -> State:
        return self.state

    def save(self, state: State) -> State:
        self.state = state.stamped("2026-01-01T00:00:00Z")
        return self.state


class FakeToolProbe:
    def which(self, name: str) -> str | None:
        return None

    def run(self, args: Sequence[str]) -> ProbeResult:
        return ProbeResult(returncode=0, stdout="")


def test_fakes_satisfy_protocols(workflow_data):
    assert isinstance(FakeWorkflowSource(workflow_from_dict(workflow_data)), WorkflowSource)
    assert isinstance(FakeStateStore(), StateStore)
    assert isinstance(FakeToolProbe(), ToolProbe)


def test_object_missing_methods_does_not_satisfy_protocols():
    assert not isinstance(object(), WorkflowSource)
    assert not isinstance(object(), StateStore)
    assert not isinstance(object(), ToolProbe)


def test_state_store_contract_round_trip():
    store: StateStore = FakeStateStore()
    written = store.save(State(active_task_id=None))
    assert written.updated_at is not None
    assert store.load() == written
