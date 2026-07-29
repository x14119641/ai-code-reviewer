import json
from pathlib import Path
from typing import Any

from reviewer.models import Benchmark, ExpectedIssue


VALID_SEVERITIES = {"low", "medium", "high", "critical"}


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
    raw_issue: Any,
    *,
    definition_path: Path,
    issue_index: int,
) -> ExpectedIssue:
    location = (
        f"{definition_path}, expected_issues[{issue_index}]"
    )

    if not isinstance(raw_issue, dict):
        raise BenchmarkLoadError(
            f"Expected issue must be a JSON object: {location}"
        )
    
    category = raw_issue.get("category")
    severity = raw_issue.get("severity")
    explanation = raw_issue.get("explanation")
    
    if not isinstance(category, str) or not category.strip():
        raise BenchmarkLoadError(
            f"Expected issue field 'category' must be a "
            f"non-empty string: {location}"
        )

    if not isinstance(severity, str):
        raise BenchmarkLoadError(
            f"Expected issue field 'severity' must be a string: "
            f"{location}"
        )
    
    normalized_severity = severity.strip().lower()

    if normalized_severity not in VALID_SEVERITIES:
        allowed = ", ".join(sorted(VALID_SEVERITIES))

        raise BenchmarkLoadError(
            f"Invalid expected severity '{severity}' at {location}. "
            f"Allowed values: {allowed}"
        )

    if not isinstance(explanation, str) or not explanation.strip():
        raise BenchmarkLoadError(
            f"Expected issue field 'explanation' must be a "
            f"non-empty string: {location}"
        )

    return ExpectedIssue(
        category=category.strip().lower(),
        severity=normalized_severity,
        explanation=explanation.strip(),
    )