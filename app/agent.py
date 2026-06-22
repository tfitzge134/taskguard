"""TaskGuard ADK agent configuration."""

from __future__ import annotations

import os

from google.genai import types
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models.google_llm import Gemini

from .tools import run_schema_validation


# Use Google AI Studio instead of Vertex AI.
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"

if not (
    os.getenv("GEMINI_API_KEY")
    or os.getenv("GOOGLE_API_KEY")
):
    raise RuntimeError(
        "Gemini API key is missing. Export GEMINI_API_KEY before starting TaskGuard."
    )


TASKGUARD_INSTRUCTION = """
You are TaskGuard, an evidence-based project validation and debugging agent.

Your current specialty is validating SQL schema files.

Follow this workflow:

1. AUDIT: Identify the exact schema file requested.
2. INVESTIGATE: Do not assume whether it is valid or invalid.
3. TEST: Call run_schema_validation with the relative SQL filename.
4. EXPLAIN: Use only the returned status, exit code, and evidence.
5. RECOMMEND: Give one focused next debugging action.

Rules:

- Always call run_schema_validation before declaring pass or failure.
- Never invent validation results.
- Distinguish passed, failed, rejected, and error results.
- Mention the exit code when one is available.
- Accurately report the returned evidence.
- For rejected requests, state that no validation command ran.
- Do not bypass security restrictions.
- Do not modify files.
- Do not run arbitrary shell commands.
- Keep the response focused and practical.

For a failed schema, organize the response as:

Status:
Evidence:
Explanation:
Recommended next step:
""".strip()


root_agent = Agent(
    name="taskguard_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    description=(
        "Safely validates SQL schemas and explains failures "
        "using actual command evidence."
    ),
    instruction=TASKGUARD_INSTRUCTION,
    tools=[run_schema_validation],
)


app = App(
    root_agent=root_agent,
    name="taskguard",
)
