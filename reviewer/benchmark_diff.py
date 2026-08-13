import difflib

from reviewer.models import DiffBenchmark, DiffReviewInput


def build_benchmark_diff(
    before_source: str,
    after_source: str,
    *,
    path: str,
) -> str:
    before_lines = before_source.splitlines(keepends=True)
    after_lines = after_source.splitlines(keepends=True)

    diff_lines = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=10,
    )

    return "".join(diff_lines)


def build_diff_review_input(
    benchmark: DiffBenchmark,
) -> DiffReviewInput:
    return DiffReviewInput(
        diff=build_benchmark_diff(
            benchmark.before_source,
            benchmark.after_source,
            path=benchmark.after_path.name,
        ),
        current_code=benchmark.after_source,
    )
