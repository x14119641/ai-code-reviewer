from reviewer.models import BenchmarkCase, BenchmarkEvaluation, CodeReview


def _find_matching_issue(
    benchmark: BenchmarkCase,
    review: CodeReview,
):
    for expected in benchmark.expected_issues:
        for actual in review.issues:
            if expected.rule == actual.rule:
                return expected, actual

    return None


def evaluate_benchmark(
    benchmark: BenchmarkCase,
    review: CodeReview,
) -> BenchmarkEvaluation:
    """
    A benchmark passes when the model correctly detects the
    presence or absence of an expected issue and matches its
    rule and category.

    Severity is evaluated separately and does not determine
    whether the benchmark passes.
    """
    expected_issue_count = len(benchmark.expected_issues)
    actual_issue_count = len(review.issues)

    expects_issues = benchmark.expects_issues
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

    if expects_issues:
        passed = (
            rule_matched
            and category_matched
            and not false_negative
        )
    else:
        passed = not false_positive

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