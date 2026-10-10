import pytest
from jsonschema import Draft202012Validator

from agentflow.constants import (
    CONFIG_SCHEMA_FILE,
    STATE_SCHEMA_FILE,
    WORKFLOW_SCHEMA_FILE,
    HistoryEvent,
    StepKind,
    StepStatus,
    TaskStatus,
)
from agentflow.validation import load_schema, schema_errors

ALL_SCHEMAS = [WORKFLOW_SCHEMA_FILE, STATE_SCHEMA_FILE, CONFIG_SCHEMA_FILE]


@pytest.mark.parametrize("name", ALL_SCHEMAS)
def test_schema_files_are_valid_json_schemas(name):
    Draft202012Validator.check_schema(load_schema(name))


def test_samples_are_valid(workflow_data, state_data, config_data):
    assert schema_errors(workflow_data, WORKFLOW_SCHEMA_FILE) == []
    assert schema_errors(state_data, STATE_SCHEMA_FILE) == []
    assert schema_errors(config_data, CONFIG_SCHEMA_FILE) == []


# Schema enums must match the Python enums exactly.
def test_schema_enums_match_python_enums():
    workflow = load_schema(WORKFLOW_SCHEMA_FILE)
    assert workflow["$defs"]["step"]["properties"]["kind"]["enum"] == [k.value for k in StepKind]
    task = load_schema(STATE_SCHEMA_FILE)["$defs"]["task"]["properties"]
    assert task["status"]["enum"] == [s.value for s in TaskStatus]
    assert task["step_status"]["enum"] == [s.value for s in StepStatus]
    entry = load_schema(STATE_SCHEMA_FILE)["$defs"]["history_entry"]["properties"]
    assert entry["event"]["enum"] == [e.value for e in HistoryEvent]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.pop("family"),
        lambda d: d.update(extra=1),
        lambda d: d.update(steps=[]),
        lambda d: d["steps"][0].update(id="Bad Id"),
        lambda d: d["steps"][0].update(kind="other"),
        lambda d: d["steps"][3].pop("loop"),  # loop step without loop spec
        lambda d: d["steps"][3].update(on_fail="fix"),  # loop step with on_fail
        lambda d: d["steps"][1].update(loop={"back_to": "build", "max_rounds": 1}),  # loop spec on a normal step
        lambda d: d["steps"][3]["loop"].update(max_rounds=0),
    ],
)
def test_invalid_workflows_are_rejected(workflow_data, mutate):
    mutate(workflow_data)
    assert schema_errors(workflow_data, WORKFLOW_SCHEMA_FILE) != []


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d["tasks"][0].pop("branch"),
        lambda d: d["tasks"][0].update(branch=""),
        lambda d: d["tasks"][0].update(status="paused"),
        lambda d: d["tasks"][0].update(loop_round=-1),
        lambda d: d["tasks"][0].update(id="task-1"),
        lambda d: d.update(active_task_id="nope"),
        lambda d: d["tasks"][0]["history"][0].update(event="moved"),
    ],
)
def test_invalid_states_are_rejected(state_data, mutate):
    mutate(state_data)
    assert schema_errors(state_data, STATE_SCHEMA_FILE) != []


def test_invalid_config_is_rejected(config_data):
    config_data["workflow"]["sha256"] = "not-a-hash"
    errors = schema_errors(config_data, CONFIG_SCHEMA_FILE)
    assert len(errors) == 1
    assert errors[0].startswith("workflow/sha256:")
