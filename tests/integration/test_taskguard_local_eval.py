"""Local TaskGuard evaluation using the Google ADK Runner."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


if not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
    pytest.skip(
        "GEMINI_API_KEY or GOOGLE_API_KEY is required for local evaluation.",
        allow_module_level=True,
    )


from app.agent import root_agent


DATASET_PATH = Path("tests/eval/datasets/basic-dataset.json")

# A tool-using agent can make more than one Gemini request per evaluation case.
# Space live cases to remain below the Google AI Studio free-tier rate limit.
MIN_SECONDS_BETWEEN_LIVE_CASES = 30.0
_last_live_case_started = 0.0


pytestmark = pytest.mark.filterwarnings(
    "error::pytest.PytestUnhandledThreadExceptionWarning"
)


HAS_GEMINI_API_KEY = bool(
os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
)

LIVE_GEMINI_TEST = pytest.mark.skipif(
not (
HAS_GEMINI_API_KEY
and os.getenv("RUN_LIVE_GEMINI_TESTS") == "TRUE"
),
reason=(
"Set RUN_LIVE_GEMINI_TESTS=TRUE and provide "
"GEMINI_API_KEY or GOOGLE_API_KEY."
),
)


def _load_prompts() -> dict[str, str]:
    """Load prompts from the TaskGuard evaluation dataset."""
    data = json.loads(DATASET_PATH.read_text())

    return {
        case["eval_case_id"]: case["prompt"]["parts"][0]["text"]
        for case in data["eval_cases"]
    }


EVAL_PROMPTS = _load_prompts()


def _run_taskguard(case_id: str) -> tuple[list[str], str]:
    """Run one evaluation case and return tool names plus all evidence."""
    global _last_live_case_started

    elapsed = time.monotonic() - _last_live_case_started
    remaining = MIN_SECONDS_BETWEEN_LIVE_CASES - elapsed
    if _last_live_case_started and remaining > 0:
        time.sleep(remaining)

    _last_live_case_started = time.monotonic()

    session_service = InMemorySessionService()
    user_id = f"local_eval_user_{case_id}"
    app_name = "taskguard_local_evaluation"

    session = session_service.create_session_sync(
        user_id=user_id,
        app_name=app_name,
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name=app_name,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=EVAL_PROMPTS[case_id],
            )
        ],
    )

    events = list(
        runner.run(
            new_message=message,
            user_id=user_id,
            session_id=session.id,
            run_config=RunConfig(
                streaming_mode=StreamingMode.SSE,
            ),
        )
    )

    assert events, f"Expected ADK events for evaluation case {case_id}."

    tool_names: list[str] = []
    response_parts: list[str] = []
    tool_results: list[str] = []

    for event in events:
        if not event.content or not event.content.parts:
            continue

        for part in event.content.parts:
            function_call = getattr(part, "function_call", None)
            if function_call and function_call.name:
                tool_names.append(function_call.name)

            function_response = getattr(part, "function_response", None)
            if function_response and function_response.response is not None:
                tool_results.append(str(function_response.response))

            if part.text:
                response_parts.append(part.text)

    combined_evidence = "\n".join(response_parts + tool_results).lower()
    return tool_names, combined_evidence


def _assert_any(text: str, *phrases: str) -> None:
    """Assert that at least one acceptable phrase appears."""
    assert any(phrase in text for phrase in phrases), (
    )


def test_evaluation_dataset_has_expected_cases() -> None:
    """The dataset must contain the five planned TaskGuard scenarios."""
    assert set(EVAL_PROMPTS) == {
        "valid_schema_passes",
        "invalid_schema_reports_all_evidence",
        "directory_traversal_rejected",
        "non_sql_file_rejected",
        "missing_schema_rejected",
    }


@LIVE_GEMINI_TEST
def test_local_eval_valid_schema() -> None:
    tool_names, evidence = _run_taskguard("valid_schema_passes")

    assert "run_schema_validation" in tool_names
    assert "passed" in evidence
    assert "schema validation passed" in evidence
    _assert_any(
        evidence,
        "exit code 0",
        "'exit_code': 0",
        '"exit_code": 0',
    )


@LIVE_GEMINI_TEST
def test_local_eval_invalid_schema() -> None:
    tool_names, evidence = _run_taskguard(
        "invalid_schema_reports_all_evidence"
    )

    assert "run_schema_validation" in tool_names
    assert "failed" in evidence
    _assert_any(
        evidence,
        "exit code 1",
        "'exit_code': 1",
        '"exit_code": 1',
    )
    assert "drop table" in evidence
    assert "userprofile" in evidence
    assert "snake_case" in evidence
    assert "posts" in evidence
    assert "primary key" in evidence


@LIVE_GEMINI_TEST
def test_local_eval_directory_traversal() -> None:
    tool_names, evidence = _run_taskguard(
        "directory_traversal_rejected"
    )

    assert "run_schema_validation" in tool_names
    assert "rejected" in evidence
    assert "directory traversal" in evidence
    _assert_any(
        evidence,
        "no validation command was executed",
        "command was not executed",
        "'command_executed': false",
        '"command_executed": false',
    )


@LIVE_GEMINI_TEST
def test_local_eval_non_sql_file() -> None:
    tool_names, evidence = _run_taskguard("non_sql_file_rejected")

    assert "run_schema_validation" in tool_names
    assert "rejected" in evidence
    _assert_any(
        evidence,
        "only .sql files",
        "only sql files",
        "must be a .sql file",
    )


@LIVE_GEMINI_TEST
def test_local_eval_missing_schema() -> None:
    tool_names, evidence = _run_taskguard("missing_schema_rejected")

    assert "run_schema_validation" in tool_names
    assert "rejected" in evidence
    _assert_any(
        evidence,
        "does not exist",
        "not found",
    )
    _assert_any(
        evidence,
        "no file was modified",
        "file was not modified",
        "'file_modified': false",
        '"file_modified": false',
    )
