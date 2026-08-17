from collections.abc import Iterable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from reviewer.benchmark_diff import (
    DiffReviewFunction,
    review_diff_benchmark,
)
from reviewer.benchmarks import load_diff_benchmark
from reviewer.evaluator import evaluate_benchmark
from reviewer.models import (
    BenchmarkEvaluation,
    BenchmarkFailure,
    BenchmarkRun,
    CodeReview,
    InferenceConfig,
    Issue,
)


def run_diff_benchmark(
    benchmark_path: Path, review_function: DiffReviewFunction
) -> BenchmarkEvaluation:
    benchmark = load_diff_benchmark(benchmark_path)

    review = review_diff_benchmark(benchmark, review_function)

    return evaluate_benchmark(
        benchmark,
        review,
    )


def run_diff_benchmarks(
    benchmark_paths: Iterable[Path],
    review_function: DiffReviewFunction,
    *,
    model: str,
    prompt_version: str,
    inference: InferenceConfig  | None = None,
) -> BenchmarkRun:
    start_time = perf_counter()

    evaluations: list[BenchmarkEvaluation] = []
    failures: list[BenchmarkFailure] = []
    
    if inference is None:
        inference = InferenceConfig()

    for benchmark_path in benchmark_paths:
        benchmark = load_diff_benchmark(benchmark_path)

        try:
            review = review_diff_benchmark(
                benchmark,
                review_function,
            )
        except RuntimeError as exc:
            failures.append(
                BenchmarkFailure(
                    benchmark=benchmark,
                    error_type=type(exc).__name__,
                    message=str(exc),
                )
            )
            continue

        evaluation = evaluate_benchmark(
            benchmark,
            review,
        )

        evaluations.append(evaluation)

    duration_seconds = perf_counter() - start_time

    return BenchmarkRun(
        model=model,
        prompt_version=prompt_version,
        evaluations=tuple(evaluations),
        failures=tuple(failures),
        duration_seconds=duration_seconds,
        created_at=datetime.now(UTC),
        inference=inference,
    )


def find_diff_benchmarks(
    benchmark_directory: Path,
) -> tuple[Path, ...]:
    benchmark_directory = benchmark_directory.resolve()
    if not benchmark_directory.exists():
        raise FileNotFoundError(
            f"Diff benchmark directory does not exist: {benchmark_directory}"
        )
    if not benchmark_directory.is_dir():
        raise NotADirectoryError(
            f"Diff benchmark path is not a directory: {benchmark_directory}"
        )
    return tuple(
        sorted(
            definition_path.parent
            for definition_path in benchmark_directory.rglob("benchmark.json")
        )
    )


def test_discovered_diff_benchmarks_can_be_run() -> None:
    benchmark_directory = Path("diff_benchmarks/performance/list_membership_in_loop")

    benchmark_paths = find_diff_benchmarks(benchmark_directory)

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
                        recommendation="Use a set or dictionary.",
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
