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
    


def issues_match(benchmark:Benchmark, review:CodeReview)->bool:
    for expected in benchmark.expected_issues:
        for actual in review.issues:
            category_matches = (
                expected.category.lower() ==  actual.category.lower()
            )
            severity_matches = (
                expected.severity == actual.severity
            )
            if category_matches and severity_matches:
                return True
    return False
    
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
    
    
    correct_issue = (
        not expects_issues or issues_match(benchmark, review)
    )
    
    passed = (
        not false_positive and not false_negative and correct_issue
    )
    
    return BenchmarkEvaluation(
        benchmark=benchmark,
        review=review,
        expected_issue_count=expected_issue_count,
        actual_issue_count=actual_issue_count,
        false_positive=false_positive,
        false_negative=false_negative,
        passed=passed,
    )