from pathlib import Path

from reviewer.diff_benchmark_runner import run_diff_benchmark
from reviewer.models import CodeReview, Issue


def test_run_one_diff_benchmark() -> None:
    benchmark_path = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_list"
    )

    def fake_review_function(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return CodeReview(
            issues=[
                Issue(
                    severity="medium",
                    category="performance",
                    rule="list_membership_in_loop",
                    title="List membership in loop",
                    explanation="Repeated list membership inside a loop.",
                    recommendation="Use a set or dictionary for membership lookup.",
                )
            ]
        )

    evaluation = run_diff_benchmark(
        benchmark_path,
        fake_review_function,
    )

    assert evaluation.passed is True


def test_run_safe_diff_benchmark_passes_with_no_issues() -> None:
    benchmark_path = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_dict_safe"
    )

    def fake_review_function(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        return CodeReview(issues=[])

    evaluation = run_diff_benchmark(
        benchmark_path,
        fake_review_function,
    )

    assert evaluation.passed is True
    assert evaluation.false_positive is False
    assert evaluation.false_negative is False
