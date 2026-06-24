"""Deterministic tests for the TaskGuard evaluation dataset."""

import json
from pathlib import Path


DATASET_PATH = Path("tests/eval/datasets/basic-dataset.json")


def test_evaluation_dataset_has_expected_cases() -> None:
    """The dataset must contain the five planned TaskGuard scenarios."""
    data = json.loads(DATASET_PATH.read_text())
    case_ids = {case["eval_case_id"] for case in data["eval_cases"]}

    assert case_ids == {
        "valid_schema_passes",
        "invalid_schema_reports_all_evidence",
        "directory_traversal_rejected",
        "non_sql_file_rejected",
        "missing_schema_rejected",
    }
