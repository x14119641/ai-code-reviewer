from pathlib import Path
from typing import Any

from reviewer.models import (
    BenchmarkResult,
    BenchmarkResultSummary,
    ResultProblemType,
)
from reviewer.result_analysis import inspect_result


def make_result(
    evaluations: list[dict[str, Any]],
) -> BenchmarkResult:
    """Create a minimal exported benchmark result for analysis tests."""

    summary = BenchmarkResultSummary(
        source=Path("results/v1/test-model.json"),
        prompt_version="v1",
        model="test-model",
        benchmark_count=len(evaluations),
        passed=0,
        failed=len(evaluations),
        false_positives=0,
        false_negatives=0,
        rule_mismatches=0,
        errors=0,
        accuracy=0.0,
        duration_seconds=1.0,
        severity_matches=0,
        severity_evaluated_count=0,
        severity_accuracy=0.0,
    )

    return BenchmarkResult(
        summary=summary,
        evaluations=evaluations,
    )


def make_evaluation(
    *,
    false_positive: bool = False,
    false_negative: bool = False,
    rule_matched: bool = True,
    category_matched: bool = True,
    severity_matched: bool = True,
    passed: bool = True,
    expected_issue_count: int = 1,
    actual_issue_count: int = 1,
) -> dict[str, Any]:
    """Create a minimal exported benchmark evaluation."""

    return {
        "benchmark": {
            "name": "Example benchmark",
            "code_path": "benchmarks/example.py",
            "source_code": "def example():\n    pass",
            "expected_issues": [],
        },
        "review": {
            "issues": [],
        },
        "expected_issue_count": expected_issue_count,
        "actual_issue_count": actual_issue_count,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "rule_matched": rule_matched,
        "category_matched": category_matched,
        "severity_matched": severity_matched,
        "passed": passed,
    }


def test_inspect_result_detects_false_positive() -> None:
    evaluation = make_evaluation(
        false_positive=True,
        rule_matched=False,
        category_matched=False,
        severity_matched=False,
        passed=False,
        expected_issue_count=0,
        actual_issue_count=1,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert len(problems) == 1
    assert problems[0].problem_type is ResultProblemType.FALSE_POSITIVE
    assert problems[0].evaluation is evaluation


def test_inspect_result_detects_false_negative() -> None:
    evaluation = make_evaluation(
        false_negative=True,
        rule_matched=False,
        category_matched=False,
        severity_matched=False,
        passed=False,
        expected_issue_count=1,
        actual_issue_count=0,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert len(problems) == 1
    assert problems[0].problem_type is ResultProblemType.FALSE_NEGATIVE
    assert problems[0].evaluation is evaluation


def test_inspect_result_detects_severity_mismatch() -> None:
    evaluation = make_evaluation(
        severity_matched=False,
        passed=True,
        expected_issue_count=1,
        actual_issue_count=1,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert len(problems) == 1
    assert problems[0].problem_type is ResultProblemType.SEVERITY_MISMATCH


def test_inspect_result_returns_no_problems_for_successful_evaluation() -> None:
    evaluation = make_evaluation()
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert problems == []


def test_false_positive_is_not_reported_as_other_mismatches() -> None:
    evaluation = make_evaluation(
        false_positive=True,
        rule_matched=False,
        category_matched=False,
        severity_matched=False,
        passed=False,
        expected_issue_count=0,
        actual_issue_count=1,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert [problem.problem_type for problem in problems] == [
        ResultProblemType.FALSE_POSITIVE
    ]


def test_false_negative_is_not_reported_as_other_mismatches() -> None:
    evaluation = make_evaluation(
        false_negative=True,
        rule_matched=False,
        category_matched=False,
        severity_matched=False,
        passed=False,
        expected_issue_count=1,
        actual_issue_count=0,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert [problem.problem_type for problem in problems] == [
        ResultProblemType.FALSE_NEGATIVE
    ]


def test_inspect_result_detects_rule_and_category_mismatches() -> None:
    evaluation = make_evaluation(
        rule_matched=False,
        category_matched=False,
        severity_matched=True,
        passed=False,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert [problem.problem_type for problem in problems] == [
        ResultProblemType.RULE_MISMATCH,
        ResultProblemType.CATEGORY_MISMATCH,
    ]


def test_severity_is_not_evaluated_without_expected_issue() -> None:
    evaluation = make_evaluation(
        severity_matched=False,
        passed=True,
        expected_issue_count=0,
        actual_issue_count=1,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert problems == []


def test_severity_is_not_evaluated_without_actual_issue() -> None:
    evaluation = make_evaluation(
        severity_matched=False,
        passed=True,
        expected_issue_count=1,
        actual_issue_count=0,
    )
    result = make_result([evaluation])

    problems = inspect_result(result)

    assert problems == []