from dataclasses import dataclass

from reviewer.benchmarks import Benchmark
from reviewer.models import CodeReview


@dataclass(frozen=True)
class BenchmarkEvaluation:
    benchmark: Benchmark
    review: CodeReview
    expected_issue_count: int
    actual_issue_count: int
    false_positive: bool
    false_negative: bool
    passed: bool
    

def evaluate_benchmark(
    benchmark: Benchmark,
    review: CodeReview,
) -> BenchmarkEvaluation:
    expected_issue_count = len(benchmark.expected_issues)
    actual_issue_count = len(review.issues)
    
    expects_issues = expected_issue_count >0
    detected_issues = actual_issue_count>0
    
    false_positive = not expects_issues and detected_issues
    false_negative = expects_issues and not detected_issues
    
    return BenchmarkEvaluation(
        benchmark=benchmark,
        review=review,
        expected_issue_count=expected_issue_count,
        actual_issue_count=actual_issue_count,
        false_positive=false_positive,
        false_negative=false_negative,
        passed=not false_positive and not false_negative,
    )