import json
from pathlib import Path
from typing import Any
from typer.testing import CliRunner


import pytest

from main import app

from reviewer.benchmark_schema import BENCHMARK_SCHEMA_VERSION
from reviewer.result_comparison import (
    ResultComparisonError,
    extract_category_from_evaluation,
    extract_rule_from_evaluation,
    find_result_files,
    load_result,
    load_result_summaries,
    load_result_summary,
    summarize_categories,
    summarize_rules,
)

runner = CliRunner()


def write_result(
    path: Path,
    *,
    model: str = "qwen3.5:9b",
    accuracy: float = 0.8,
    severity_matches: int = 3,
    severity_evaluated_count: int = 4,
    severity_accuracy: float = 0.75,
    failures: list[dict[str, str]] | None = None,
    evaluations: list[dict[str, Any]] | None = None,
) -> None:
    data = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "model": model,
        "evaluations": evaluations or [],
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
                "schema_version": BENCHMARK_SCHEMA_VERSION,
                "model": "qwen3.5:9b",
                "failures": [],
                "evaluations": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ResultComparisonError,
        match="benchmark_count",
    ):
        load_result_summary(result_file)


def test_extract_rule_uses_expected_issue() -> None:
    evaluation = {
        "benchmark": {
            "code_path": "benchmarks/security/sql_injection/example.py",
            "expected_issues": [
                {
                    "rule": "sql_injection",
                }
            ],
        }
    }

    assert extract_rule_from_evaluation(evaluation) == "sql_injection"


def test_extract_rule_uses_directory_for_safe_benchmark() -> None:
    evaluation = {
        "benchmark": {
            "code_path": (
                "benchmarks/security/sql_injection/" "parameterized_query.py"
            ),
            "expected_issues": [],
        }
    }

    assert extract_rule_from_evaluation(evaluation) == "sql_injection"


def test_extract_rule_ignores_legacy_directories() -> None:
    evaluation = {
        "benchmark": {
            "code_path": ("benchmarks/false_positives/" "clean_user_lookup.py"),
            "expected_issues": [],
        }
    }

    assert extract_rule_from_evaluation(evaluation) is None


def test_extract_rule_ignores_python_directory() -> None:
    evaluation = {
        "benchmark": {
            "code_path": "benchmarks/python/mutable_default.py",
            "expected_issues": [],
        }
    }

    assert extract_rule_from_evaluation(evaluation) is None


def test_summarize_rules_aggregates_results() -> None:
    evaluations = [
        {
            "benchmark": {
                "code_path": ("benchmarks/security/sql_injection/" "unsafe.py"),
                "expected_issues": [
                    {
                        "rule": "sql_injection",
                    }
                ],
            },
            "passed": True,
            "false_positive": False,
            "false_negative": False,
        },
        {
            "benchmark": {
                "code_path": ("benchmarks/security/sql_injection/" "safe.py"),
                "expected_issues": [],
            },
            "passed": False,
            "false_positive": True,
            "false_negative": False,
        },
    ]

    summaries = summarize_rules(evaluations)

    assert len(summaries) == 1

    summary = summaries[0]

    assert summary.rule == "sql_injection"
    assert summary.benchmark_count == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.false_positives == 1
    assert summary.false_negatives == 0
    assert summary.accuracy == 0.5


def test_load_result_summary_rejects_invalid_failures(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"

    data = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "model": "qwen3.5:9b",
        "evaluations": [],
        "failures": 2,
        "benchmark_count": 5,
        "passed": 3,
        "failed": 2,
        "false_positives": 1,
        "false_negatives": 1,
        "accuracy": 0.6,
        "severity_matches": 2,
        "severity_evaluated_count": 3,
        "severity_accuracy": 2 / 3,
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


def test_load_result_includes_evaluations(
    tmp_path: Path,
) -> None:
    result_file = tmp_path / "result.json"

    data = {
        "schema_version": BENCHMARK_SCHEMA_VERSION,
        "model": "qwen3.5:9b",
        "evaluations": [
            {
                "passed": True,
            }
        ],
        "failures": [],
        "benchmark_count": 1,
        "passed": 1,
        "failed": 0,
        "false_positives": 0,
        "false_negatives": 0,
        "accuracy": 1.0,
        "severity_matches": 1,
        "severity_evaluated_count": 1,
        "severity_accuracy": 1.0,
        "duration_seconds": 2.0,
    }

    result_file.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    result = load_result(result_file)

    assert result.summary.model == "qwen3.5:9b"
    assert result.evaluations == [{"passed": True}]


def test_compare_results_by_rule_displays_rule_table(
    tmp_path: Path,
) -> None:
    write_result(
        tmp_path / "result.json",
        model="qwen3.5:9b",
        evaluations=[
            {
                "benchmark": {
                    "code_path": ("benchmarks/security/sql_injection/" "unsafe.py"),
                    "expected_issues": [
                        {
                            "rule": "sql_injection",
                        }
                    ],
                },
                "passed": True,
                "false_positive": False,
                "false_negative": False,
            }
        ],
    )

    result = runner.invoke(
        app,
        [
            "compare-results",
            str(tmp_path),
            "--by-rule",
        ],
    )

    assert result.exit_code == 0
    assert "Rule Comparison" in result.stdout
    assert "sql_injection" in result.stdout
    assert "100.0%" in result.stdout


def test_extract_category_uses_expected_issue() -> None:
    evaluation = {
        "benchmark": {
            "code_path": ("benchmarks/security/sql_injection/example.py"),
            "expected_issues": [
                {
                    "category": "security",
                }
            ],
        }
    }

    assert extract_category_from_evaluation(evaluation) == "security"


def test_summarize_categories_aggregates_results() -> None:
    evaluations = [
        {
            "benchmark": {
                "code_path": ("benchmarks/security/sql_injection/" "unsafe.py"),
                "expected_issues": [
                    {
                        "category": "security",
                    }
                ],
            },
            "passed": True,
            "false_positive": False,
            "false_negative": False,
        },
        {
            "benchmark": {
                "code_path": ("benchmarks/security/sql_injection/" "safe.py"),
                "expected_issues": [],
            },
            "passed": False,
            "false_positive": True,
            "false_negative": False,
        },
    ]

    summaries = summarize_categories(evaluations)

    assert len(summaries) == 1

    summary = summaries[0]

    assert summary.category == "security"
    assert summary.benchmark_count == 2
    assert summary.passed == 1
    assert summary.failed == 1
    assert summary.false_positives == 1
    assert summary.false_negatives == 0
    assert summary.accuracy == 0.5
