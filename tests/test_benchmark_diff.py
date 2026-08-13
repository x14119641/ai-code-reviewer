from pathlib import Path

from reviewer.benchmark_diff import (
    build_benchmark_diff,
    build_diff_review_input,
    review_diff_benchmark,
)
from reviewer.benchmarks import load_diff_benchmark
from reviewer.models import CodeReview


def test_build_benchmark_diff_contains_changed_lines() -> None:
    before_source = """\
def find_users(users: dict[str, int]) -> None:
    pass
"""

    after_source = """\
def find_users(users: list[str]) -> None:
    pass
"""

    diff = build_benchmark_diff(before_source, after_source, path="example.py")

    assert "-def find_users(users: dict[str, int]) -> None:" in diff
    assert "+def find_users(users: list[str]) -> None:" in diff


def test_build_benchmark_diff_uses_git_style_file_headers() -> None:
    before_source = "value = 1\n"
    after_source = "value = 2\n"

    diff = build_benchmark_diff(
        before_source,
        after_source,
        path="example.py",
    )

    assert "--- a/example.py" in diff
    assert "+++ b/example.py" in diff


def test_build_benchmark_diff_returns_empty_string_when_sources_are_identical() -> None:
    source = "value = 1\n"

    diff = build_benchmark_diff(
        source,
        source,
        path="example.py",
    )

    assert diff == ""


def test_build_diff_review_input_uses_after_source_as_current_code() -> None:
    benchmark_path = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_list"
    )

    benchmark = load_diff_benchmark(benchmark_path)

    review_input = build_diff_review_input(benchmark)

    assert review_input.current_code == benchmark.after_source


def test_build_diff_review_input_builds_diff_from_before_to_after() -> None:
    benchmark_path = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_list"
    )

    benchmark = load_diff_benchmark(benchmark_path)

    review_input = build_diff_review_input(benchmark)

    assert "-    users: dict[str, int]," in review_input.diff
    assert "+    users: list[str]," in review_input.diff


def test_review_diff_benchmark_passes_diff_and_current_code() -> None:
    benchmark_path = (
        Path("diff_benchmarks")
        / "performance"
        / "list_membership_in_loop"
        / "dict_to_list"
    )

    benchmark = load_diff_benchmark(benchmark_path)

    received_diff = ""
    received_current_code = ""

    def fake_review_function(
        diff: str,
        current_code: str,
    ) -> CodeReview:
        nonlocal received_diff
        nonlocal received_current_code

        received_diff = diff
        received_current_code = current_code

        return CodeReview(issues=[])

    review = review_diff_benchmark(
        benchmark,
        fake_review_function,
    )

    assert "-    users: dict[str, int]," in received_diff
    assert "+    users: list[str]," in received_diff
    assert received_current_code == benchmark.after_source
    assert review == CodeReview(issues=[])