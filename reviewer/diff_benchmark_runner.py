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
) -> BenchmarkRun:
    start_time = perf_counter()

    evaluations: list[BenchmarkEvaluation] = []
    failures: list[BenchmarkFailure] = []

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
    )
