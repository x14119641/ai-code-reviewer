import json
from pathlib import Path
from typing import Any, cast

from reviewer.models import Benchmark, ExpectedIssue
from reviewer.taxonomy import (
    VALID_CATEGORIES,
    VALID_RULES,
    VALID_SEVERITIES,
    IssueCategory,
    IssueRule,
    Severity,
)


class BenchmarkLoadError(ValueError):
    """Raised when a benchmark definition cannot be loaded or validated."""


    

def load_benchmark(code_path:Path) -> Benchmark:
    """Load a benchmark source file and its matchin JSON definition.
    
    Example:
        benchmarks/security/sql_injection.py
        benchmarks/security/sql_injection.json
    """
    
    code_path = code_path.resolve()
    
    if not code_path.exists():
        raise BenchmarkLoadError(
            f"Benchmark code file does not exist: {code_path}"
        )

    if not code_path.is_file():
        raise BenchmarkLoadError(
            f"Benchmark code path is not a file: {code_path}"
        )

    if code_path.suffix != ".py":
        raise BenchmarkLoadError(
            f"Benchmark code file must be a Python file: {code_path}"
        )

    definition_path = code_path.with_suffix(".json")
    if not definition_path.exists():
        raise BenchmarkLoadError(
            f"Benchmark definition does not exist: {definition_path}"
        )

    try:
        source_code = code_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BenchmarkLoadError(
            f"Could not read benchmark code file: {code_path}"
        ) from exc

    try:
        raw_definition = definition_path.read_text(encoding="utf-8")
        definition = json.loads(raw_definition)
    except OSError as exc:
        raise BenchmarkLoadError(
            f"Could not read benchmark definition: {definition_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise BenchmarkLoadError(
            f"Invalid JSON in benchmark definition "
            f"{definition_path}: {exc.msg}"
        ) from exc

    return _build_benchmark(
        code_path=code_path,
        source_code=source_code,
        definition=definition,
        definition_path=definition_path,
    )
    

def _build_benchmark(
    *,
    code_path: Path,
    source_code: str,
    definition: Any,
    definition_path: Path,
) -> Benchmark:
    if not isinstance(definition, dict):
        raise BenchmarkLoadError(
            f"Benchmark definition must be a JSON object: {definition_path}"
        )

    name = definition.get("name")

    if not isinstance(name, str) or not name.strip():
        raise BenchmarkLoadError(
            f"Benchmark field 'name' must be a non-empty string: "
            f"{definition_path}"
        )

    raw_expected_issues = definition.get("expected_issues")

    if not isinstance(raw_expected_issues, list):
        raise BenchmarkLoadError(
            f"Benchmark field 'expected_issues' must be a list: "
            f"{definition_path}"
        )

    expected_issues = tuple(
        _build_expected_issue(
            raw_issue,
            definition_path=definition_path,
            issue_index=index,
        )
        for index, raw_issue in enumerate(raw_expected_issues)
    )

    return Benchmark(
        name=name.strip(),
        code_path=code_path,
        source_code=source_code,
        expected_issues=expected_issues,
    )
    

def _build_expected_issue(
    data: Any,
    *,
    definition_path: Path,
    issue_index: int,
) -> ExpectedIssue:
    if not isinstance(data, dict):
        raise BenchmarkLoadError(
            f"Expected issue {issue_index} must be a JSON object: "
            f"{definition_path}"
        )

    severity = data.get("severity")
    rule = data.get("rule")
    category = data.get("category")
    explanation = data.get("explanation")

    if category not in VALID_CATEGORIES:
        raise BenchmarkLoadError(
            f"Expected issue {issue_index} has invalid category "
            f"{category!r}: {definition_path}"
        )

    if rule not in VALID_RULES:
        raise BenchmarkLoadError(
            f"Expected issue {issue_index} has invalid rule "
            f"{rule!r}: {definition_path}"
        )

    if severity not in VALID_SEVERITIES:
        raise BenchmarkLoadError(
            f"Expected issue {issue_index} has invalid severity "
            f"{severity!r}: {definition_path}"
        )

    if not isinstance(explanation, str) or not explanation.strip():
        raise BenchmarkLoadError(
            f"Expected issue {issue_index} field 'explanation' "
            f"must be a non-empty string: {definition_path}"
        )

    return ExpectedIssue(
        severity=cast(Severity, severity),
        rule=cast(IssueRule, rule),
        category=cast(IssueCategory, category),
        explanation=explanation.strip(),
    )