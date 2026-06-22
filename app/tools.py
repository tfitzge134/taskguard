"""Safe deterministic tools used by the TaskGuard agent."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VALIDATOR_PATH = PROJECT_ROOT / "validate_schema.py"


def run_schema_validation(schema_file: str) -> dict[str, Any]:
    """Validate one SQL schema file inside the TaskGuard project.

    This tool rejects absolute paths, directory traversal, non-SQL files,
    and files located outside the approved project directory.

    Args:
        schema_file: Relative path to an SQL file inside the project.

    Returns:
        A structured result containing status, command, exit code,
        standard output, standard error, and supporting evidence.
    """
    requested_path = Path(schema_file)

    if requested_path.is_absolute():
        return _rejected_result(
            schema_file,
            "Absolute paths are not allowed.",
        )

    if ".." in requested_path.parts:
        return _rejected_result(
            schema_file,
            "Directory traversal is not allowed.",
        )

    if requested_path.suffix.lower() != ".sql":
        return _rejected_result(
            schema_file,
            "Only .sql files can be validated.",
        )

    resolved_file = (PROJECT_ROOT / requested_path).resolve()

    try:
        resolved_file.relative_to(PROJECT_ROOT)
    except ValueError:
        return _rejected_result(
            schema_file,
            "The requested file is outside the approved project directory.",
        )

    if not resolved_file.is_file():
        return _rejected_result(
            schema_file,
            "The requested SQL file does not exist.",
        )

    command = [
        sys.executable,
        str(VALIDATOR_PATH),
        str(resolved_file),
    ]

    try:
        completed = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "schema_file": schema_file,
            "command_run": " ".join(command),
            "exit_code": None,
            "stdout": "",
            "stderr": "Schema validation timed out after 10 seconds.",
            "evidence": ["Schema validation timed out after 10 seconds."],
            "file_modified": False,
        }

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()

    evidence = [
        line
        for line in (stdout + "\n" + stderr).splitlines()
        if line.strip()
    ]

    return {
        "status": "passed" if completed.returncode == 0 else "failed",
        "schema_file": schema_file,
        "command_run": f"python validate_schema.py {schema_file}",
        "exit_code": completed.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "evidence": evidence,
        "file_modified": False,
    }


def _rejected_result(schema_file: str, reason: str) -> dict[str, Any]:
    """Return a consistent result for a blocked request."""
    return {
        "status": "rejected",
        "schema_file": schema_file,
        "command_run": "",
        "exit_code": None,
        "stdout": "",
        "stderr": reason,
        "evidence": [reason],
        "file_modified": False,
    }
