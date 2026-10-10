"""Shared test data. Step ids here are sample data for a made-up family, not foundation values."""

import copy
import subprocess
from pathlib import Path
from typing import Any

import pytest
import yaml

SAMPLE_WORKFLOW: dict[str, Any] = {
    "schema_version": 1,
    "family": "sample",
    "max_rounds": 2,
    "steps": [
        {"id": "confirm", "name": "Confirm", "role": "lead", "requires_approval": True},
        {"id": "build", "name": "Build", "role": "builder"},
        {"id": "check", "name": "Check", "role": "checker", "on_fail": "build"},
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


@pytest.fixture(autouse=True)
def _git_stays_in_tmp(tmp_path, monkeypatch):
    # git must never walk up from a temp dir into a real repository.
    monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path))


@pytest.fixture
def git_repo(tmp_path) -> Path:
    repo = tmp_path / "project"
    repo.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    return repo


def write_workflow(path: Path, data: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return path


@pytest.fixture
def workflow_file(tmp_path, workflow_data) -> Path:
    # Outside the project repo, like a workflow shipped in an installed plugin.
    return write_workflow(tmp_path / "plugin" / "workflow.yaml", workflow_data)
