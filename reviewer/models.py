from pathlib import Path
from dataclasses import dataclass

from reviewer.taxonomy import IssueCategory, IssueRule, Severity


@dataclass
class Issue:
    severity: Severity
    category: IssueCategory
    rule: IssueRule
    title: str
    explanation: str
    recommendation: str


@dataclass
class CodeReview:
    issues: list[Issue]


@dataclass
class ExpectedIssue:
    severity: Severity
    rule: IssueRule
    category: IssueCategory
    explanation: str


@dataclass(frozen=True)
class Benchmark:
    name: str
    code_path: Path
    source_code: str
    expected_issues: tuple[ExpectedIssue, ...]

    @property
    def expects_issues(self) -> bool:
        return bool(self.expected_issues)


@dataclass(frozen=True)
class BenchmarkEvaluation:
    benchmark: Benchmark
    review: CodeReview
    expected_issue_count: int
    actual_issue_count: int
    false_positive: bool
    false_negative: bool
    rule_matched: bool
    category_matched: bool
    severity_matched: bool
    passed: bool
