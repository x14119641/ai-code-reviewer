from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from reviewer.benchmarks import load_benchmark
from reviewer.evaluator import evaluate_benchmark
from reviewer.models import (
    BenchmarkRun,
    CodeReview,
    BenchmarkEvaluation,
    BenchmarkFailure,
)

ReviewFunction = Callable[[Path], CodeReview]


def find_benchmark_files(
    benchmark_directory: Path,
) -> tuple[Path, ...]:
    if not benchmark_directory.exists():
        raise FileNotFoundError(
            f"Benchmark directory does not exist: " f"{benchmark_directory}"
        )

    if not benchmark_directory.is_dir():
        raise NotADirectoryError(
            f"Benchmark path is not a directory: " f"{benchmark_directory}"
        )

    return tuple(sorted(benchmark_directory.rglob("*.py")))


def run_benchmarks(
    benchmark_paths: Iterable[Path], review_function: ReviewFunction, *, model: str
) -> BenchmarkRun:
    start_time = perf_counter()
    evaluations: list[BenchmarkEvaluation] = []
    failures: list[BenchmarkFailure] = []

    for code_path in benchmark_paths:
        benchmark = load_benchmark(code_path)
        try:
            review = review_function(benchmark.code_path)
        except RuntimeError as exc:
            failures.append(
                BenchmarkFailure(benchmark=benchmark, error_type=type(exc).__name__, message=str(exc))
            )
            continue
        evaluation = evaluate_benchmark(
            benchmark,
            review,
        )

        evaluations.append(evaluation)
    duration_seconds = perf_counter() - start_time
    return BenchmarkRun(
        model=model, evaluations=tuple(evaluations), duration_seconds=duration_seconds, failures=tuple(failures), created_at=datetime.now(UTC),
    )
