import json
from pathlib import Path

import pytest

from reviewer.benchmark_schema import BENCHMARK_SCHEMA_VERSION
from reviewer.result_comparison import (
    ResultComparisonError,
    find_result_files,
    load_result_summaries,
    load_result_summary,
)


def write_result(
    path: Path,
    *,
    model: str = "qwen3.5:9b",
    accuracy: float = 0.8,
    severity_matches: int = 3,
    severity_evaluated_count: int = 4,
    severity_accuracy: float = 0.75,
    failures: list[dict[str, str]] | None = None,
) -> None:
    data = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "model": model,
        "evaluations": [],
        "failures": failures or [],
        "benchmark_count": 5,
        "passed": 4,
        "failed": 1,
        "false_positives": 1,
        "false_negatives": 0,
        "accuracy": accuracy,
        "severity_matches": severity_matches,
        "severity_evaluated_count": severity_evaluated_count,
        "severity_accuracy": severity_accuracy,
        "duration_seconds": 12.5,
    }

    path.write_text(
        json.dumps(data),
        encoding="utf-8",
    )


def test_find_result_files_returns_sorted_json_files(
    tmp_path: Path,
) -> None:
    write_result(tmp_path / "second.json")
    write_result(tmp_path / "first.json")
    (tmp_path / "notes.txt").write_text("ignored", encoding="utf-8")

    result = find_result_files(tmp_path)

    assert result == [
        tmp_path / "first.json",
        tmp_path / "second.json",
    ]


def test_find_result_files_rejects_missing_directory(
    tmp_path: Path,
) -> None:
    missing_directory = tmp_path / "missing"

    with pytest.raises(
        ResultComparisonError,
        match="does not exist",
    ):
        find_result_files(missing_directory)


def test_find_result_files_rejects_file_path(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"
    write_result(result_file)

    with pytest.raises(
        ResultComparisonError,
        match="not a directory",
    ):
        find_result_files(result_file)


def test_find_result_files_rejects_empty_directory(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ResultComparisonError,
        match="No JSON result files",
    ):
        find_result_files(tmp_path)


def test_load_result_summary(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"

    write_result(
        result_file,
        model="qwen2.5-coder:7b",
        accuracy=0.8,
        severity_matches=3,
        severity_evaluated_count=4,
        severity_accuracy=0.75,
        failures=[
            {
                "path": "benchmarks/example.py",
                "error": "Invalid JSON",
            }
        ],
    )

    summary = load_result_summary(result_file)

    assert summary.source == result_file
    assert summary.model == "qwen2.5-coder:7b"
    assert summary.benchmark_count == 5
    assert summary.passed == 4
    assert summary.failed == 1
    assert summary.false_positives == 1
    assert summary.false_negatives == 0
    assert summary.errors == 1
    assert summary.accuracy == 0.8
    assert summary.severity_matches == 3
    assert summary.severity_evaluated_count == 4
    assert summary.severity_accuracy == 0.75
    assert summary.duration_seconds == 12.5


def test_load_result_summaries_loads_all_files(
    tmp_path: Path,
) -> None:
    write_result(
        tmp_path / "qwen.json",
        model="qwen3.5:9b",
    )
    write_result(
        tmp_path / "coder.json",
        model="qwen2.5-coder:7b",
    )

    summaries = load_result_summaries(tmp_path)

    assert [summary.model for summary in summaries] == [
        "qwen2.5-coder:7b",
        "qwen3.5:9b",
    ]


def test_load_result_summary_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "invalid.json"
    result_file.write_text("{invalid", encoding="utf-8")

    with pytest.raises(
        ResultComparisonError,
        match="Invalid JSON",
    ):
        load_result_summary(result_file)


def test_load_result_summary_rejects_missing_field(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"
    result_file.write_text(
        json.dumps(
            {
                "model": "qwen3.5:9b",
                "failures": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ResultComparisonError,
        match="benchmark_count",
    ):
        load_result_summary(result_file)


def test_load_result_summary_rejects_invalid_failures(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"

    data = {
        "model": "qwen3.5:9b",
        "failures": 2,
        "benchmark_count": 5,
        "passed": 3,
        "failed": 2,
        "false_positives": 1,
        "false_negatives": 1,
        "accuracy": 60.0,
        "duration_seconds": 20.0,
    }

    result_file.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    with pytest.raises(
        ResultComparisonError,
        match="'failures' must be a list",
    ):
        load_result_summary(result_file)