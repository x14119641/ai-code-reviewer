from pathlib import Path

from reviewer.benchmarks import Benchmark
from reviewer.evaluator import evaluate_benchmark
from reviewer.models import CodeReview


def test_clean_benchmark_passes_with_clean_review() -> None:
    benchmark = Benchmark(
        name="Clean example",
        code_path=Path("clean_example.py"),
        source_code="def add(a, b):\n    return a + b\n",
        expected_issues=(),
    )

    review = CodeReview(issues=[])

    evaluation = evaluate_benchmark(benchmark, review)

    assert evaluation.passed is True
    assert evaluation.false_positive is False
    assert evaluation.false_negative is False
    assert evaluation.expected_issue_count == 0
    assert evaluation.actual_issue_count == 0