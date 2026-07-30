from reviewer.models import (
    Benchmark,
    BenchmarkEvaluation,
    CodeReview,
    ExpectedIssue,
    Issue,
)


def _find_matching_issue(
    benchmarck: Benchmark,
    review: CodeReview,
) -> tuple[ExpectedIssue, Issue] | None:
    for expected in benchmarck.expects_issues():
        for actual in review.issues:
            if expected.rule == actual.rule:
                return expected, actual
    return None


def evaluate_benchmark(benchmark: Benchmark, review: CodeReview) -> BenchmarkEvaluation:
    expected_issue_count = len(benchmark.expected_issues)
    actual_issue_count = len(review.issues)

    expects_issues = expected_issue_count > 0
    detected_issues = actual_issue_count > 0

    false_positive = not expects_issues and detected_issues
    false_negative = expects_issues and not detected_issues

    matching_pair = _find_matching_issue(
        benchmark=benchmark,
        review=review,
    )

    rule_matched = matching_pair is not None

    if matching_pair is None:
        category_matched = False
        severity_matched = False
    else:
        expected, actual = matching_pair
        category_matched = expected.category == actual.category
        severity_matched = expected.severity == actual.severity

    if not expects_issues:
        passed = not detected_issues
    else:
        passed = rule_matched

    return BenchmarkEvaluation(
        benchmark=benchmark,
        review=review,
        expected_issue_count=expected_issue_count,
        actual_issue_count=actual_issue_count,
        false_positive=false_positive,
        false_negative=false_negative,
        rule_matched=rule_matched,
        category_matched=category_matched,
        severity_matched=severity_matched,
        passed=passed,
    )
