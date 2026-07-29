from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

from reviewer.benchmarks import Benchmark, load_benchmark
from reviewer.evaluator import BenchmarkEvaluation, evaluate_benchmark
from reviewer.models import CodeReview


ReviewFunction = Callable[[Path], CodeReview]


@dataclass(frozen=True)
class BenchmarkRun:
    evaluations : tuple[BenchmarkEvaluation, ...]
    
    @property
    def total(self) ->int:
        return len(self.evaluations)
    
    @property
    def passed(self) ->int:
        return sum(evaluation.passed for evaluation in self.evaluations)
    
    @property
    def failed(self)-> int:
        return self.total-self.passed
    
    @property
    def false_positives(self)->int:
        return sum(evaluation.false_positive
            for evaluation in self.evaluations)
    
    @property
    def false_negatives(self) -> int:
        return sum(
            evaluation.false_negative
            for evaluation in self.evaluations
        )

    @property
    def accuracy(self) -> float:
        if self.total == 0:
            return 0.0

        return self.passed / self.total
    

def find_benchmark_files(
    benchmark_directory: Path,
) -> tuple[Path, ...]:
    if not benchmark_directory.exists():
        raise FileNotFoundError(
            f"Benchmark directory does not exist: "
            f"{benchmark_directory}"
        )

    if not benchmark_directory.is_dir():
        raise NotADirectoryError(
            f"Benchmark path is not a directory: "
            f"{benchmark_directory}"
        )

    return tuple(
        sorted(benchmark_directory.rglob("*.py"))
    )
    
def run_benchmarks(
    benchmark_paths: Iterable[Path],
    review_function: ReviewFunction,
) -> BenchmarkRun:
    evaluations: list[BenchmarkEvaluation] = []

    for code_path in benchmark_paths:
        benchmark = load_benchmark(code_path)
        review = review_function(benchmark.code_path)

        evaluation = evaluate_benchmark(
            benchmark,
            review,
        )

        evaluations.append(evaluation)

    return BenchmarkRun(
        evaluations=tuple(evaluations),
    )