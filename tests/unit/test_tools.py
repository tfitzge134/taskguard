"""Unit tests for TaskGuard's safe schema-validation tool."""

import importlib.util
from pathlib import Path


TOOLS_PATH = Path(__file__).resolve().parents[2] / "app" / "tools.py"

spec = importlib.util.spec_from_file_location("taskguard_tools", TOOLS_PATH)
tools = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(tools)


def test_good_schema_passes():
    result = tools.run_schema_validation("good_schema.sql")

    assert result["status"] == "passed"
    assert result["exit_code"] == 0
    assert result["evidence"] == ["Schema validation passed."]
    assert result["file_modified"] is False


def test_bad_schema_reports_expected_failures():
    result = tools.run_schema_validation("bad_schema.sql")

    assert result["status"] == "failed"
    assert result["exit_code"] == 1
    assert result["file_modified"] is False

    evidence = "\n".join(result["evidence"])

    assert "DROP TABLE" in evidence
    assert "userProfile" in evidence
    assert "snake_case" in evidence
    assert "posts" in evidence
    assert "primary key named 'id'" in evidence


def test_directory_traversal_is_rejected():
    result = tools.run_schema_validation("../bad_schema.sql")

    assert result["status"] == "rejected"
    assert result["exit_code"] is None
    assert result["command_run"] == ""
    assert result["evidence"] == ["Directory traversal is not allowed."]
    assert result["file_modified"] is False
