from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
import json
from pathlib import Path
from typing import Any
from reviewer.models import BenchmarkRun

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def serialize_path(path: Path) -> str:
    """Return a project-relative path when possible."""
    resolved_path = path.resolve()

    try:
        return str(resolved_path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(resolved_path)


def to_json_compatible(value: Any) -> Any:
    """Convert project objects into values supported by JSON."""
    if is_dataclass(value):
        return to_json_compatible(asdict(value))
    if isinstance(value, Path):
        return serialize_path(value)

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {str(key): to_json_compatible(item) for key, item in value.items()}

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, (list, tuple)):
        return [to_json_compatible(item) for item in value]

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    raise TypeError(f"Cannot serialize value of type {type(value).__name__}")


def benchmark_run_to_dict(run: BenchmarkRun) -> dict[str, Any]:
    """Convert a benchmark run into a JSON-compatible dictionary."""
    data = to_json_compatible(run)

    data.update(
        {
            "benchmark_count": run.benchmark_count,
            "passed": run.passed,
            "failed": run.failed,
            "failure_count": run.failure_count,
            "false_positives": run.false_positives,
            "false_negatives": run.false_negatives,
            "accuracy": run.accuracy,
            "duration_seconds": round(run.duration_seconds, 2),
            "created_at": run.created_at.isoformat(),
        }
    )

    return data


def save_benchmark_run(run: BenchmarkRun, output_path: Path) -> None:
    """Save a benchmark run as formatted JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    data = benchmark_run_to_dict(run)

    output_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-"
    )
