from pathlib import Path

from reviewer.benchmark_diff import (
    DiffReviewFunction,
    review_diff_benchmark,
)
from reviewer.benchmarks import load_diff_benchmark
from reviewer.evaluator import evaluate_benchmark
from reviewer.models import BenchmarkEvaluation


def run_diff_benchmark(
    benchmark_path: Path, review_function: DiffReviewFunction
) -> BenchmarkEvaluation:
    benchmark = load_diff_benchmark(benchmark_path)

    review = review_diff_benchmark(benchmark, review_function)

    return evaluate_benchmark(
        benchmark,
        review,
    )
