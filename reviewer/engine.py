from pathlib import Path
from dataclasses import dataclass
from reviewer.models import Issue, CodeReview
from reviewer.taxonomy import (
    IssueCategory,
    IssueRule,
    Severity,
    VALID_CATEGORIES,
    VALID_RULES,
    VALID_SEVERITIES,
)

from reviewer.llm import generate_review
from reviewer.prompts import build_review_prompt
from collections.abc import Iterable, Iterator

from typing import Any, cast
import json

IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__"}

VALID_SEVERITIES = ["low", "medium", "high", "critical"]


@dataclass
class ReviewResult:
    path: Path
    review: CodeReview | None
    error: str | None = None


def clean_json_response(response: str) -> str:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned

def find_python_files(path: Path) -> list[Path]:
    """Find Python files recursively, excluding ignored directories."""
    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path}")
    if not path.is_dir():
        raise ValueError(f"Not a directory: {path}")

    files = [
        file
        for file in path.rglob("*.py")
        if not any(part in IGNORED_DIRECTORIES for part in file.parts)
    ]
    return sorted(files)


def parse_review_response(response: str) -> CodeReview:
    cleaned_response = clean_json_response(response)
    try:
        data: Any = json.loads(cleaned_response)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"The model returned invalid JSON:\n\n{response}"
        ) from exc

    if not isinstance(data, dict):
        raise RuntimeError("The model response must be a JSON object.")

    issues_data = data.get("issues")

    if not isinstance(issues_data, list):
        raise RuntimeError("The model response must contain an 'issues' list.")

    issues: list[Issue] = []

    for index, item in enumerate(issues_data):
        if not isinstance(item, dict):
            raise RuntimeError(f"Issue {index} must be a JSON object.")

        required_fields = {
            "severity",
            "rule",
            "category",
            "title",
            "explanation",
            "recommendation",
        }

        missing_fields = required_fields - item.keys()

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise RuntimeError(
                f"Issue {index} is missing required fields: {missing}"
            )

        severity = item["severity"]
        category = item["category"]
        rule = item["rule"]

        if severity not in VALID_SEVERITIES:
            raise RuntimeError(
                f"Issue {index} has invalid severity: {severity}"
            )

        if category not in VALID_CATEGORIES:
            raise RuntimeError(
                f"Issue {index} has invalid category: {category}"
            )

        if rule not in VALID_RULES:
            raise RuntimeError(
                f"Issue {index} has invalid rule: {rule}"
            )

        issues.append(
            Issue(
                severity=cast(Severity, severity),
                rule=cast(IssueRule, rule),
                category=cast(IssueCategory, category),
                title=item["title"],
                explanation=item["explanation"],
                recommendation=item["recommendation"],
            )
        )

    return CodeReview(issues=issues)



def review_file(
    path: Path,
    model: str,
) -> CodeReview:
    """Read and review one source-code file"""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    try:
        code = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise

    prompt = build_review_prompt(code)

    response = generate_review(prompt=prompt, model=model)

    return parse_review_response(response)


def review_folder(path: Path, model: str) -> Iterator[ReviewResult]:
    """Review all Python files found in a directory."""
    files = find_python_files(path=path)

    yield from review_files(files, model)


def review_files(files: Iterable[Path], model: str) -> Iterator[ReviewResult]:
    """Review an iterable of Python files one at a time."""
    for file in files:
        review = review_file(file, model)
        yield ReviewResult(path=file, review=review)
