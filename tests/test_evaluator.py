from pathlib import Path

from reviewer.benchmarks import Benchmark
from reviewer.evaluator import evaluate_benchmark
from reviewer.models import CodeReview, ExpectedIssue, Issue


def test_clean_benchmark_passes_with_clean_review() -> None:
    benchmark = Benchmark(
        name="Clean example",
        code_path=Path("clean_example.py"),
        source_code="def add(a, b):\n    return a + b\n",
        expected_issues=(),
    )

    review = CodeReview(issues=[])

    evaluation = evaluate_benchmark(benchmark, review)

    assert evaluation.passed is True
    assert evaluation.false_positive is False
    assert evaluation.false_negative is False
    assert evaluation.expected_issue_count == 0
    assert evaluation.actual_issue_count == 0
    
    
def test_category_mismatch_fails_benchmark() -> None:
    benchmark = Benchmark(
        name="Mutable default argument",
        code_path=Path("mutable_default.py"),
        source_code=(
            "def add_item(item: str, items: list[str] = []) -> list[str]:\n"
            "    items.append(item)\n"
            "    return items\n"
        ),
        expected_issues=(
            ExpectedIssue(
                severity="medium",
                rule="mutable_default_argument",
                category="bug",
                explanation="A mutable default argument shares state across calls.",
            ),
        ),
    )

    review = CodeReview(
        issues=[
            Issue(
                severity="medium",
                rule="mutable_default_argument",
                category="maintainability",
                title="Mutable default argument",
                explanation="The default list is shared across calls.",
                recommendation="Use None and create the list inside the function.",
            ),
        ]
    )

    evaluation = evaluate_benchmark(
        benchmark=benchmark,
        review=review,
    )

    assert evaluation.rule_matched is True
    assert evaluation.category_matched is False
    assert evaluation.severity_matched is True
    assert evaluation.passed is False
    
    
    
    
def test_wrong_rule_is_classified_as_rule_mismatch() -> None:
    benchmark = Benchmark(
        name="Expected duplicate code",
        code_path=Path("example.py"),
        source_code="value = 1",
        expected_issues=(
            ExpectedIssue(
                severity="low",
                rule="duplicate_code",
                category="maintainability",
                explanation="Expected duplicate code.",
            ),
        ),
    )

    review = CodeReview(
        issues=[
            Issue(
                severity="medium",
                category="bug",
                rule="mutable_default_argument",
                title="Wrong issue",
                explanation="Wrong rule returned.",
                recommendation="Example recommendation.",
            )
        ]
    )

    evaluation = evaluate_benchmark(benchmark, review)

    assert evaluation.passed is False
    assert evaluation.false_positive is False
    assert evaluation.false_negative is False
    assert evaluation.rule_mismatch is True
    assert evaluation.rule_matched is False