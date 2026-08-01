import json
from pathlib import Path
from typing import Any

from reviewer.models import (
    BenchmarkResultSummary,
    RuleComparisonSummary,
    BenchmarkResult,
)

IGNORED_RULE_DIRECTORIES = {
    "false_positives",
    "python",
}


class ResultComparisonError(ValueError):
    """Raised when benchmark result files cannot be compared"""


def find_result_files(directory: Path) -> list[Path]:
    """Return benchmark result JSON files from a directory."""

    if not directory.exists():
        raise ResultComparisonError(f"Results directory does not exist: {directory}")

    if not directory.is_dir():
        raise ResultComparisonError(f"Results path is not a directory: {directory}")

    result_files = sorted(directory.glob("*.json"))

    if not result_files:
        raise ResultComparisonError(f"No JSON result files found in: {directory}")

    return result_files


def load_result(path: Path) -> BenchmarkResult:
    """Load one exported benchmark result file."""

    try:
        raw_data = path.read_text(encoding="utf-8")
    except OSError as error:
        raise ResultComparisonError(
            f"Could not read result file {path}: {error}"
        ) from error

    try:
        data = json.loads(raw_data)
    except json.JSONDecodeError as error:
        raise ResultComparisonError(
            f"Invalid JSON in result file {path}: {error}"
        ) from error

    if not isinstance(data, dict):
        raise ResultComparisonError(f"Expected a JSON object in result file: {path}")

    failures = _require_list(data, "failures", path)
    evaluations = _require_list(data, "evaluations", path)

    summary = BenchmarkResultSummary(
        source=path,
        model=_require_string(data, "model", path),
        benchmark_count=_require_integer(data, "benchmark_count", path),
        passed=_require_integer(data, "passed", path),
        failed=_require_integer(data, "failed", path),
        false_positives=_require_integer(data, "false_positives", path),
        false_negatives=_require_integer(data, "false_negatives", path),
        errors=len(failures),
        accuracy=_require_number(data, "accuracy", path),
        duration_seconds=_require_number(
            data,
            "duration_seconds",
            path,
        ),
        severity_matches=_require_integer(
            data,
            "severity_matches",
            path,
        ),
        severity_evaluated_count=_require_integer(
            data,
            "severity_evaluated_count",
            path,
        ),
        severity_accuracy=_require_number(
            data,
            "severity_accuracy",
            path,
        ),
    )

    return BenchmarkResult(
        summary=summary,
        evaluations=evaluations,
    )


def load_result_summary(path: Path) -> BenchmarkResultSummary:
    """Load only the summary from one benchmark result file."""

    return load_result(path).summary


def load_results(directory: Path) -> list[BenchmarkResult]:
    """Load all benchmark result files from a directory."""

    return [load_result(path) for path in find_result_files(directory)]


def load_result_summaries(
    directory: Path,
) -> list[BenchmarkResultSummary]:
    """Load all benchmark result summaries from a directory."""

    return [result.summary for result in load_results(directory)]


def _require_string(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> str:
    value = data.get(field)

    if not isinstance(value, str) or not value:
        raise ResultComparisonError(
            f"Field '{field}' must be a non-empty string in {path}"
        )

    return value


def _require_integer(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> int:
    value = data.get(field)

    # bool is a subclass of int, so reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, int):
        raise ResultComparisonError(f"Field '{field}' must be an integer in {path}")

    if value < 0:
        raise ResultComparisonError(f"Field '{field}' cannot be negative in {path}")

    return value


def _require_number(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> float:
    value = data.get(field)

    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ResultComparisonError(f"Field '{field}' must be a number in {path}")

    if value < 0:
        raise ResultComparisonError(f"Field '{field}' cannot be negative in {path}")

    return float(value)


def _require_list(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> list[Any]:
    value = data.get(field)

    if not isinstance(value, list):
        raise ResultComparisonError(f"Field '{field}' must be a list in {path}")

    return value


def extract_rule_from_evaluation(evaluation: dict[str, Any]) -> str | None:
    benchmark = evaluation.get("benchmark")

    if not isinstance(benchmark, dict):
        return None

    expected_issues = benchmark.get("expected_issues")

    if isinstance(expected_issues, list) and expected_issues:
        first_issue = expected_issues[0]

        if isinstance(first_issue, dict):
            rule = first_issue.get("rule")

            if isinstance(rule, str) and rule:
                return rule

    code_path = benchmark.get("code_path")

    if not isinstance(code_path, str):
        return None

    path = Path(code_path)

    # Example:
    # benchmarks/security/sql_injection/example.py
    if len(path.parts) >= 3:
        rule = path.parent.name

        if rule in IGNORED_RULE_DIRECTORIES:
            return None

        return rule

    return None


def summarize_rules(
    evaluations: list[dict[str, Any]],
) -> list[RuleComparisonSummary]:
    grouped: dict[str, list[dict[str, Any]]] = {}

    for evaluation in evaluations:
        rule = extract_rule_from_evaluation(evaluation)

        if rule is None:
            continue

        grouped.setdefault(rule, []).append(evaluation)

    summaries = []

    for rule, rule_evaluations in grouped.items():
        passed = sum(
            evaluation.get("passed") is True for evaluation in rule_evaluations
        )

        false_positives = sum(
            evaluation.get("false_positive") is True for evaluation in rule_evaluations
        )

        false_negatives = sum(
            evaluation.get("false_negative") is True for evaluation in rule_evaluations
        )

        benchmark_count = len(rule_evaluations)

        summaries.append(
            RuleComparisonSummary(
                rule=rule,
                benchmark_count=benchmark_count,
                passed=passed,
                failed=benchmark_count - passed,
                false_positives=false_positives,
                false_negatives=false_negatives,
            )
        )

    return sorted(
        summaries,
        key=lambda summary: summary.rule,
    )
