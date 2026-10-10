"""Shared test data. Step ids here are sample data for a made-up family, not foundation values."""

import copy
from typing import Any

import pytest

SAMPLE_WORKFLOW: dict[str, Any] = {
    "schema_version": 1,
    "family": "sample",
    "steps": [
        {"id": "confirm", "name": "Confirm", "role": "lead", "requires_approval": True},
        {"id": "build", "name": "Build", "role": "builder"},
        {"id": "check", "name": "Check", "role": "checker", "on_fail": "fix"},
        {
            "id": "fix",
            "name": "Fix",
            "role": "builder",
            "kind": "loop",
            "loop": {"back_to": "build", "max_rounds": 2},
        },
    ],
}

SAMPLE_STATE: dict[str, Any] = {
    "schema_version": 1,
    "updated_at": "2026-10-10T08:00:00Z",
    "active_task_id": "T-001",
    "tasks": [
        {
            "id": "T-001",
            "title": "Do the thing",
            "status": "open",
            "current_step": "check",
            "step_status": "failed",
            "loop_round": 1,
            "branch": "feature/thing",
            "history": [{"at": "2026-10-10T07:00:00Z", "step": "confirm", "event": "approved"}],
        }
    ],
}

SAMPLE_CONFIG: dict[str, Any] = {
    "schema_version": 1,
    "workflow": {"family": "sample", "source_path": "/somewhere/workflow.yaml", "sha256": "0" * 64},
}


@pytest.fixture
def workflow_data() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_WORKFLOW)


@pytest.fixture
def state_data() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_STATE)


@pytest.fixture
def config_data() -> dict[str, Any]:
    return copy.deepcopy(SAMPLE_CONFIG)
