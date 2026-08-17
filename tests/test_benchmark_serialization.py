import json
from datetime import UTC, datetime
from pathlib import Path

from reviewer.benchmark_serialization import (
    PROJECT_ROOT,
    benchmark_run_to_dict,
    save_benchmark_run,
    serialize_path,
    to_json_compatible,
)
from reviewer.models import (
    Benchmark,
    BenchmarkEvaluation,
    BenchmarkFailure,
    BenchmarkRun,
    CodeReview,
    DiffBenchmark,
    ExpectedIssue,
    Issue,
)
from reviewer.prompts import DEFAULT_PROMPT_VERSION


def test_to_json_compatible_converts_paths_and_tuples() -> None:
    value = {
        "path": Path("benchmarks/example.py"),
        "rules": ("sql_injection", "shell_injection"),
    }

    result = to_json_compatible(value)

    assert result == {
        "path": "benchmarks/example.py",
        "rules": ["sql_injection", "shell_injection"],
    }

    # It must also be accepted by Python's JSON encoder.
    json.dumps(result)


def test_serialize_path_returns_project_relative_path() -> None:
    path = PROJECT_ROOT / "benchmarks" / "example.py"

    result = serialize_path(path)

    assert result == "benchmarks/example.py"


def test_serialize_path_keeps_external_path() -> None:
    path = Path("/tmp/example.py")

    result = serialize_path(path)

    assert result == "/tmp/example.py"


def test_benchmark_run_to_dict_includes_results_and_summary() -> None:
    benchmark = Benchmark(
        name="Mutable default argument",
        code_path=PROJECT_ROOT / "benchmarks" / "example.py",
        source_code="def example(items=[]):\n    return items",
        expected_issues=[
            ExpectedIssue(
                severity="medium",
                rule="mutable_default_argument",
                category="bug",
                explanation="Mutable default argument.",
            )
        ],
    )

    review = CodeReview(
        issues=[
            Issue(
                severity="medium",
                category="bug",
                rule="mutable_default_argument",
                title="Mutable default argument",
                explanation="The list is shared between calls.",
                recommendation="Use None as the default.",
            )
        ]
    )

    evaluation = BenchmarkEvaluation(
        benchmark=benchmark,
        review=review,
        expected_issue_count=1,
        actual_issue_count=1,
        false_positive=False,
        false_negative=False,
        rule_matched=True,
        rule_mismatch=False,
        category_matched=True,
        severity_matched=True,
        passed=True,
    )

    run = BenchmarkRun(
        model="test-model",
        evaluations=[evaluation],
        duration_seconds=1.234,
        failures=[],
        created_at=datetime.now(UTC),
        prompt_version=DEFAULT_PROMPT_VERSION,
    )

    result = benchmark_run_to_dict(run)

    assert result["model"] == "test-model"
    assert result["duration_seconds"] == 1.23
    assert result["benchmark_count"] == 1
    assert result["passed"] == 1
    assert result["failed"] == 0
    assert result["failure_count"] == 0
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0
    assert result["accuracy"] == 1.0
    assert result["prompt_version"] == DEFAULT_PROMPT_VERSION

    assert result["evaluations"][0]["benchmark"]["code_path"] == (
        "benchmarks/example.py"
    )

    json.dumps(result)


def test_save_benchmark_run_writes_json_file(tmp_path: Path) -> None:
    run = BenchmarkRun(
        model="test-model",
        evaluations=[],
        duration_seconds=2.5,
        failures=[],
        created_at=datetime.now(UTC),
        prompt_version=DEFAULT_PROMPT_VERSION,
    )

    output_path = tmp_path / "results" / "benchmark.json"

    save_benchmark_run(run, output_path)

    assert output_path.exists()

    data = json.loads(output_path.read_text(encoding="utf-8"))

    assert data["model"] == "test-model"
    assert data["prompt_version"] == DEFAULT_PROMPT_VERSION
    assert data["duration_seconds"] == 2.5
    assert data["benchmark_count"] == 0
    assert data["passed"] == 0
    assert data["failed"] == 0
    assert data["evaluations"] == []
    assert data["failures"] == []


def test_benchmark_run_to_dict_serializes_failures() -> None:
    benchmark = Benchmark(
        name="Broken response",
        code_path=PROJECT_ROOT / "benchmarks" / "broken.py",
        source_code="def broken():\n    pass",
        expected_issues=[],
    )

    failure = BenchmarkFailure(
        benchmark=benchmark,
        error_type="RuntimeError",
        message="Invalid model response",
    )

    run = BenchmarkRun(
        model="test-model",
        evaluations=[],
        duration_seconds=1.0,
        failures=[failure],
        created_at=datetime.now(UTC),
        prompt_version=DEFAULT_PROMPT_VERSION,
    )

    result = benchmark_run_to_dict(run)

    assert result["benchmark_count"] == 1
    assert result["passed"] == 0
    assert result["failed"] == 1
    assert result["failure_count"] == 1
    assert result["prompt_version"] == DEFAULT_PROMPT_VERSION

    assert result["failures"][0]["error_type"] == "RuntimeError"
    assert result["failures"][0]["message"] == "Invalid model response"
    assert result["failures"][0]["benchmark"]["code_path"] == ("benchmarks/broken.py")


def test_to_json_compatible_serializes_datetime() -> None:
    created_at = datetime(2026, 7, 31, 16, 0, tzinfo=UTC)

    result = to_json_compatible(created_at)

    assert result == "2026-07-31T16:00:00+00:00"


def test_benchmark_run_to_dict_serializes_diff_benchmark() -> None:
    before_path = Path("diff_benchmarks/example/before.py")
    after_path = Path("diff_benchmarks/example/after.py")

    benchmark = DiffBenchmark(
        name="Example diff benchmark",
        before_path=before_path,
        after_path=after_path,
        before_source="value = 1\n",
        after_source="value = 2\n",
        expected_issues=(),
    )

    review = CodeReview(issues=[])

    evaluation = BenchmarkEvaluation(
        benchmark=benchmark,
        review=review,
        expected_issue_count=0,
        actual_issue_count=0,
        false_positive=False,
        false_negative=False,
        rule_matched=False,
        rule_mismatch=False,
        category_matched=False,
        severity_matched=False,
        passed=True,
    )

    run = BenchmarkRun(
        created_at=datetime.now(UTC),
        model="test-model",
        prompt_version="v9",
        evaluations=(evaluation,),
        duration_seconds=1.0,
    )

    data = benchmark_run_to_dict(run)

    serialized_benchmark = data["evaluations"][0]["benchmark"]

    assert serialized_benchmark["before_path"].endswith(
        "diff_benchmarks/example/before.py"
    )
    assert serialized_benchmark["after_path"].endswith(
        "diff_benchmarks/example/after.py"
    )
