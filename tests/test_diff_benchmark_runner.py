from pathlib import Path

import pytest

from reviewer.diff_benchmark_runner import (
    find_diff_benchmarks,
    run_diff_benchmark,
    run_diff_benchmarks,
)
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


def test_find_diff_benchmarks_finds_benchmark_directories() -> None:
    benchmark_directory = Path("diff_benchmarks")

    benchmark_paths = find_diff_benchmarks(benchmark_directory)

    expected_positive = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_list"
    ).resolve()

    expected_safe = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_dict_safe"
    ).resolve()

    assert expected_positive in benchmark_paths
    assert expected_safe in benchmark_paths
    

def test_find_diff_benchmarks_raises_when_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    benchmark_directory = tmp_path / "missing"

    with pytest.raises(
        FileNotFoundError,
        match="Diff benchmark directory does not exist",
    ):
        find_diff_benchmarks(benchmark_directory)
        
        
def test_find_diff_benchmarks_raises_when_path_is_not_directory(
    tmp_path: Path,
) -> None:
    benchmark_file = tmp_path / "benchmark.txt"

    benchmark_file.write_text(
        "not a directory",
        encoding="utf-8",
    )

    with pytest.raises(
        NotADirectoryError,
        match="Diff benchmark path is not a directory",
    ):
        find_diff_benchmarks(benchmark_file)