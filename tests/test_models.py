from datetime import UTC, datetime
from pathlib import Path

from reviewer.models import Benchmark, BenchmarkEvaluation, BenchmarkRun, CodeReview


def create_evaluation(
    *, passed: bool, false_positive: bool = False, false_negative: bool = False
) -> BenchmarkEvaluation:
    benchmark = Benchmark(
        name="Example benchmark",
        code_path=Path("example.py"),
        source_code="value=1",
        expected_issues=(),
    )

    return BenchmarkEvaluation(
        benchmark=benchmark,
        review=CodeReview(issues=[]),
        expected_issue_count=0,
        actual_issue_count=0,
        false_positive=false_positive,
        false_negative=false_negative,
        rule_matched=False,
        category_matched=False,
        severity_matched=False,
        passed=passed,
    )


def test_benchmark_run_calculates_summary() -> None:
    run = BenchmarkRun(
        model="test-model",
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
