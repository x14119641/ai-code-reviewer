import json
from pathlib import Path
from typing import Any

from reviewer.models import BenchmarkResultSummary


class ResultComparisonError(ValueError):
    """Raised when benchmark result files cannot be compared"""
    
    
def find_result_files(directory: Path) -> list[Path]:
    """Return benchmark result JSON files from a directory."""

    if not directory.exists():
        raise ResultComparisonError(
            f"Results directory does not exist: {directory}"
        )

    if not directory.is_dir():
        raise ResultComparisonError(
            f"Results path is not a directory: {directory}"
        )

    result_files = sorted(directory.glob("*.json"))

    if not result_files:
        raise ResultComparisonError(
            f"No JSON result files found in: {directory}"
        )

    return result_files


def load_result_summary(path: Path) -> BenchmarkResultSummary:
    """Load the comparison fields from one benchmark result file."""

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
        raise ResultComparisonError(
            f"Expected a JSON object in result file: {path}"
        )

    failures = _require_list(data, "failures", path)

    return BenchmarkResultSummary(
        source=path,
        model=_require_string(data, "model", path),
        benchmark_count=_require_integer(data, "benchmark_count", path),
        passed=_require_integer(data, "passed", path),
        failed=_require_integer(data, "failed", path),
        false_positives=_require_integer(data, "false_positives", path),
        false_negatives=_require_integer(data, "false_negatives", path),
        errors=len(failures),
        accuracy=_require_number(data, "accuracy", path),
        duration_seconds=_require_number(data, "duration_seconds", path),
    )


def load_result_summaries(directory: Path) -> list[BenchmarkResultSummary]:
    """Load all benchmark result summaries from a directory."""

    return [
        load_result_summary(path)
        for path in find_result_files(directory)
    ]


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
        raise ResultComparisonError(
            f"Field '{field}' must be an integer in {path}"
        )

    if value < 0:
        raise ResultComparisonError(
            f"Field '{field}' cannot be negative in {path}"
        )

    return value


def _require_number(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> float:
    value = data.get(field)

    if isinstance(value, bool) or not isinstance(value, int | float):
        raise ResultComparisonError(
            f"Field '{field}' must be a number in {path}"
        )

    if value < 0:
        raise ResultComparisonError(
            f"Field '{field}' cannot be negative in {path}"
        )

    return float(value)


def _require_list(
    data: dict[str, Any],
    field: str,
    path: Path,
) -> list[Any]:
    value = data.get(field)

    if not isinstance(value, list):
        raise ResultComparisonError(
            f"Field '{field}' must be a list in {path}"
        )

    return value