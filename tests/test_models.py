from datetime import UTC, datetime
from pathlib import Path

from reviewer.benchmark_schema import BENCHMARK_SCHEMA_VERSION
from reviewer.models import (
    Benchmark,
    BenchmarkEvaluation,
    BenchmarkRun,
    CodeReview,
    DiffBenchmark,
)


def create_evaluation(
    *,
    passed: bool = True,
    false_positive: bool = False,
    false_negative: bool = False,
    rule_mismatch: bool = False,
    rule_matched: bool = False,
    category_matched: bool = False,
    severity_matched: bool = False,
) -> BenchmarkEvaluation:
    benchmark = Benchmark(
        name="Example benchmark",
        code_path=Path("example.py"),
        source_code="value = 1",
        expected_issues=(),
    )

    return BenchmarkEvaluation(
        benchmark=benchmark,
        review=CodeReview(issues=[]),
        expected_issue_count=0,
        actual_issue_count=0,
        false_positive=false_positive,
        false_negative=false_negative,
        rule_matched=rule_matched,
        rule_mismatch=rule_mismatch,
        category_matched=category_matched,
        severity_matched=severity_matched,
        passed=passed,
    )


def test_benchmark_run_calculates_summary() -> None:
    run = BenchmarkRun(
        model="test-model",
        prompt_version="v1",
        evaluations=(
            create_evaluation(passed=True),
            create_evaluation(
                passed=False,
                false_positive=True,
            ),
            create_evaluation(
                passed=False,
                false_negative=True,
            ),
        ),
        duration_seconds=12.5,
        created_at=datetime.now(UTC),
    )

    assert run.model == "test-model"
    assert run.benchmark_count == 3
    assert run.passed == 1
    assert run.failed == 2
    assert run.false_positives == 1
    assert run.false_negatives == 1
    assert run.accuracy == 1 / 3
    assert run.duration_seconds == 12.5


def test_empty_benchmark_run_has_zero_accuracy() -> None:
    run = BenchmarkRun(
        model="test-model",
        prompt_version="v1",
        evaluations=(),
        duration_seconds=0.0,
        created_at=datetime.now(UTC),
    )

    assert run.benchmark_count == 0
    assert run.passed == 0
    assert run.failed == 0
    assert run.accuracy == 0.0
    assert run.model == "test-model"
    assert run.duration_seconds >= 0.0


def test_severity_metrics_count_only_rule_and_category_matches() -> None:
    run = BenchmarkRun(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        prompt_version="v1",
        created_at=datetime.now(UTC),
        model="test-model",
        evaluations=(
            create_evaluation(
                rule_matched=True,
                category_matched=True,
                severity_matched=True,
            ),
            create_evaluation(
                rule_matched=True,
                category_matched=True,
                severity_matched=False,
            ),
            create_evaluation(
                rule_matched=True,
                category_matched=False,
                severity_matched=False,
                passed=False,
            ),
            create_evaluation(
                rule_matched=False,
                category_matched=False,
                severity_matched=False,
                passed=False,
            ),
        ),
        failures=(),
        duration_seconds=1.0,
    )

    assert run.severity_evaluated_count == 2
    assert run.severity_matches == 1
    assert run.severity_accuracy == 0.5


def test_severity_accuracy_is_zero_when_nothing_is_evaluated() -> None:
    run = BenchmarkRun(
        schema_version=BENCHMARK_SCHEMA_VERSION,
        prompt_version="v1",
        created_at=datetime.now(UTC),
        model="test-model",
        evaluations=(),
        failures=(),
        duration_seconds=1.0,
    )

    assert run.severity_evaluated_count == 0
    assert run.severity_matches == 0
    assert run.severity_accuracy == 0.0


def test_benchmark_display_path_uses_code_path() -> None:
    code_path = Path("benchmarks/example.py")

    benchmark = Benchmark(
        name="Example benchmark",
        code_path=code_path,
        source_code="value = 1\n",
        expected_issues=(),
    )

    assert benchmark.display_path == code_path


def test_diff_benchmark_display_path_uses_after_path() -> None:
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

    assert benchmark.display_path == after_path



def test_benchmark_run_counts_rule_mismatches() -> None:
    run = BenchmarkRun(
        model="test-model",
        prompt_version="v1",
        evaluations=(
            create_evaluation(rule_mismatch=True, passed=False),
            create_evaluation(rule_mismatch=False),
        ),
        duration_seconds=1.0,
        created_at=datetime.now(UTC),
    )

    assert run.rule_mismatches == 1