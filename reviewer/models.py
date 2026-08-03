from datetime import datetime
from enum import StrEnum
from pathlib import Path
from dataclasses import dataclass
from typing import Any

from reviewer.benchmark_schema import BENCHMARK_SCHEMA_VERSION
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
    created_at: datetime
    model: str
    prompt_version: str
    evaluations: tuple[BenchmarkEvaluation, ...]
    duration_seconds: float
    failures: tuple[BenchmarkFailure, ...] = ()
    schema_version: int = BENCHMARK_SCHEMA_VERSION

    @property
    def benchmark_count(self) -> int:
        return len(self.evaluations) + len(self.failures)

    @property
    def passed(self) -> int:
        """Number of successful benchmark evaluations."""
        return sum(evaluation.passed for evaluation in self.evaluations)

    @property
    def completed_count(self) -> int:
        return len(self.evaluations)

    @property
    def failure_count(self) -> int:
        return len(self.failures)

    @property
    def failed(self) -> int:
        """Number of benchmarks that did not pass, including runtime failures."""
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

    @property
    def severity_matches(self) -> int:
        return sum(
            evaluation.rule_matched
            and evaluation.category_matched
            and evaluation.severity_matched
            for evaluation in self.evaluations
        )

    @property
    def severity_evaluated_count(self) -> int:
        return sum(
            evaluation.rule_matched and evaluation.category_matched
            for evaluation in self.evaluations
        )

    @property
    def severity_accuracy(self) -> float:
        if self.severity_evaluated_count == 0:
            return 0.0

        return self.severity_matches / self.severity_evaluated_count


@dataclass(frozen=True)
class BenchmarkResultSummary:
    """Summary of one exported benchmark run."""
    source: Path
    prompt_version: str
    model: str
    benchmark_count: int
    passed: int
    failed: int
    false_positives: int
    false_negatives: int
    errors: int
    accuracy: float
    duration_seconds: float
    severity_matches: int
    severity_evaluated_count: int
    severity_accuracy: float


@dataclass(frozen=True)
class BenchmarkResult:
    summary: BenchmarkResultSummary
    evaluations: list[dict[str, Any]]


@dataclass(frozen=True)
class RuleComparisonSummary:
    rule: str
    benchmark_count: int
    passed: int
    failed: int
    false_positives: int
    false_negatives: int

    @property
    def accuracy(self) -> float:
        if self.benchmark_count == 0:
            return 0.0

        return self.passed / self.benchmark_count


@dataclass(frozen=True)
class CategoryComparisonSummary:
    category: str
    benchmark_count: int
    passed: int
    failed: int
    false_positives: int
    false_negatives: int

    @property
    def accuracy(self) -> float:
        if self.benchmark_count == 0:
            return 0.0

        return self.passed / self.benchmark_count


class ResultProblemType(StrEnum):
    FALSE_POSITIVE = "false_positive"
    FALSE_NEGATIVE = "false_negative"
    RULE_MISMATCH = "rule_mismatch"
    CATEGORY_MISMATCH = "category_mismatch"
    SEVERITY_MISMATCH = "severity_mismatch"
    

@dataclass(frozen=True)
class ResultProblem:
    problem_type: ResultProblemType
    evaluation: dict[str, Any]