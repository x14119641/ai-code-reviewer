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


@dataclass(frozen=True)
class BenchmarkFailure:
    benchmark: Benchmark
    error_type: str
    message: str


@dataclass(frozen=True)
class BenchmarkRun:
    model: str
    evaluations: tuple[BenchmarkEvaluation, ...]
    duration_seconds: float
    failures: tuple[BenchmarkFailure, ...] = ()

    @property
    def benchmark_count(self) -> int:
        return len(self.evaluations) + len(self.failures)

    @property
    def passed(self) -> int:
        return sum(evaluation.passed for evaluation in self.evaluations)

    @property
    def completed_count(self) -> int:
        return len(self.evaluations)

    @property
    def failure_count(self) -> int:
        return len(self.failures)

    @property
    def failed(self) -> int:
        return self.benchmark_count - self.passed

    @property
    def false_positives(self) -> int:
        return sum(evaluation.false_positive for evaluation in self.evaluations)

    @property
    def false_negatives(self) -> int:
        return sum(evaluation.false_negative for evaluation in self.evaluations)

    @property
    def accuracy(self) -> float:
        if self.benchmark_count == 0:
            return 0.0
        return self.passed / self.benchmark_count
