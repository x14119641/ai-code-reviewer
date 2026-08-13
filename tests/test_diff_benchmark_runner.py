from pathlib import Path

from reviewer.diff_benchmark_runner import run_diff_benchmark, run_diff_benchmarks
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


def test_run_diff_benchmarks_runs_multiple_cases() -> None:
    benchmark_paths = (
        Path("diff_benchmarks/performance/" "list_membership_in_loop/dict_to_list"),
        Path(
            "diff_benchmarks/performance/" "list_membership_in_loop/dict_to_dict_safe"
        ),
    )

    def fake_review_function(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        if "users: list[str]" in current_code:
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

        return CodeReview(issues=[])

    run = run_diff_benchmarks(
        benchmark_paths,
        fake_review_function,
        model="test-model",
        prompt_version="v9",
    )

    assert run.benchmark_count == 2
    assert run.passed == 2
    assert run.failed == 0
    assert run.model == "test-model"
    assert run.prompt_version == "v9"


def test_run_diff_benchmarks_records_runtime_failures() -> None:
    benchmark_paths = (
        Path("diff_benchmarks/performance/" "list_membership_in_loop/dict_to_list"),
        Path(
            "diff_benchmarks/performance/" "list_membership_in_loop/dict_to_dict_safe"
        ),
    )

    def fake_review_function(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        if "users: dict[str, int]" in current_code:
            raise RuntimeError("LLM failed")

        return CodeReview(
            issues=[
                Issue(
                    severity="medium",
                    category="performance",
                    rule="list_membership_in_loop",
                    title="List membership in loop",
                    explanation="Repeated list membership inside a loop.",
                    recommendation="Use a set or dictionary.",
                )
            ]
        )

    run = run_diff_benchmarks(
        benchmark_paths,
        fake_review_function,
        model="test-model",
        prompt_version="v9",
    )

    assert run.benchmark_count == 2
    assert run.completed_count == 1
    assert run.failure_count == 1
    assert len(run.failures) == 1
    assert run.failures[0].error_type == "RuntimeError"
    assert run.failures[0].message == "LLM failed"
