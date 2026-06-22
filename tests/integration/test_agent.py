"""End-to-end integration tests for the TaskGuard ADK agent."""

from __future__ import annotations

import os

import pytest
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


# Integration tests require a real Gemini request.
if not (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
):
    pytest.skip(
        "GEMINI_API_KEY or GOOGLE_API_KEY is required for integration tests.",
        allow_module_level=True,
    )


from app.agent import root_agent


def test_taskguard_validates_bad_schema() -> None:
    """TaskGuard must call its tool and report actual validation evidence."""

    session_service = InMemorySessionService()

    session = session_service.create_session_sync(
        user_id="integration_test_user",
        app_name="taskguard_integration_test",
    )

    runner = Runner(
        agent=root_agent,
        session_service=session_service,
        app_name="taskguard_integration_test",
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part.from_text(
                text=(
                    "Validate bad_schema.sql. Explain every failure using "
                    "only the validation evidence and report the exit code."
                )
            )
        ],
    )

    events = list(
        runner.run(
            new_message=message,
            user_id="integration_test_user",
            session_id=session.id,
            run_config=RunConfig(
                streaming_mode=StreamingMode.SSE
            ),
        )
    )

    assert events, "Expected TaskGuard to produce ADK events."

    tool_names: list[str] = []
    response_parts: list[str] = []

    for event in events:
        if not event.content or not event.content.parts:
            continue

        for part in event.content.parts:
            function_call = getattr(part, "function_call", None)

            if function_call and function_call.name:
                tool_names.append(function_call.name)

            if part.text:
                response_parts.append(part.text)

    response = "\n".join(response_parts)
    normalized_response = response.lower()

    assert "run_schema_validation" in tool_names
    assert "failed" in normalized_response
    assert "exit code 1" in normalized_response
    assert "drop table" in normalized_response
    assert "userprofile" in normalized_response
    assert "snake_case" in normalized_response
    assert "posts" in normalized_response
    assert "primary key" in normalized_response
