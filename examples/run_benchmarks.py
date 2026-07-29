from pathlib import Path

from reviewer.benchmark_runner import find_benchmark_files, run_benchmarks
from reviewer.models import CodeReview, Issue



"""
Example showing how to execute the benchmark runner programmatically.

Equivalent CLI functionality will be available through:
    ai-review benchmark benchmarks/
"""

def fake_review(path: Path) -> CodeReview:
    print(f"Reviewing {path.name}")
    return CodeReview(issues=[])


paths = find_benchmark_files(Path("benchmarks"))

run = run_benchmarks(
    benchmark_paths=paths,
    review_function=fake_review,
)

print(f"Benchmarks: {run.total}")
print(f"Passed: {run.passed}")
print(f"Failed: {run.failed}")
print(f"Accuracy: {run.accuracy:.2%}")