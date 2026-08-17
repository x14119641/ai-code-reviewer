import json
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from reviewer.llm import REVIEW_RESPONSE_SCHEMA, generate_review
from reviewer.models import CodeReview, Issue
from reviewer.prompts import (
    DEFAULT_PROMPT_VERSION,
    build_diff_candidates_prompt,
    build_diff_prompt,
    build_review_prompt,
)
from reviewer.taxonomy import (
    RULE_SEVERITY,
    VALID_CATEGORIES,
    VALID_RULES,
    VALID_SEVERITIES,
    IssueCategory,
    IssueRule,
    Severity,
)

IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__"}


@dataclass
class ReviewResult:
    path: Path
    review: CodeReview | None
    error: str | None = None


def clean_json_response(response: str) -> str:
    cleaned = response.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json") :].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```") :].strip()

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
        raise RuntimeError(f"The model returned invalid JSON:\n\n{response}") from exc

    if not isinstance(data, dict):
        raise TypeError("The model response must be a JSON object.")

    issues_data = data.get("issues")

    if not isinstance(issues_data, list):
        raise TypeError("The model response must contain an 'issues' list.")

    issues: list[Issue] = []

    for index, item in enumerate(issues_data):
        if not isinstance(item, dict):
            raise TypeError(f"Issue {index} must be a JSON object.")

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
            raise RuntimeError(f"Issue {index} is missing required fields: {missing}")

        severity = item["severity"]
        category = item["category"]
        rule = item["rule"]

        if severity not in VALID_SEVERITIES:
            raise RuntimeError(f"Issue {index} has invalid severity: {severity}")

        if category not in VALID_CATEGORIES:
            raise RuntimeError(f"Issue {index} has invalid category: {category}")

        if rule not in VALID_RULES:
            raise RuntimeError(f"Issue {index} has invalid rule: {rule}")

        issues.append(
            Issue(
                severity=cast(Severity, RULE_SEVERITY[rule]),
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
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> CodeReview:
    """Read and review one source-code file"""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    code = path.read_text(encoding="utf-8")

    prompt = build_review_prompt(
        code,
        prompt_version=prompt_version,
    )

    response = generate_review(prompt=prompt, model=model)

    return parse_review_response(response)


def review_folder(path: Path, model: str) -> Iterator[ReviewResult]:
    """Review all Python files found in a directory."""
    files = find_python_files(path=path)

    yield from review_files(files, model)


def review_files(
    files: Iterable[Path],
    model: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> Iterator[ReviewResult]:
    """Review an iterable of Python files one at a time."""
    for file in files:
        review = review_file(file, model, prompt_version=prompt_version)
        yield ReviewResult(path=file, review=review)


def review_diff(
    diff: str,
    current_code: str,
    model: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
) -> CodeReview:
    """Review a Git diff with current source context."""
    prompt = build_diff_prompt(
        diff=diff,
        current_code=current_code,
        prompt_version=prompt_version,
    )

    response = generate_review(
        prompt=prompt,
        model=model,
    )

    return parse_review_response(response)


def build_changed_files_context(files: Iterable[Path]) -> str:
    """Build source context for changed Python files."""
    sections: list[str] = []

    for path in files:
        if not path.is_file():
            continue

        code = path.read_text(encoding="utf-8")

        sections.append(f"File: {path}\n\n{code}")

    return "\n\n".join(sections)


def find_diff_candidates(
    diff: str,
    current_code: str,
    model: str,
    prompt_version: str,
) -> CodeReview:
    """Find candidate issues in a Git diff for later verification."""
    prompt = build_diff_candidates_prompt(
        diff=diff,
        current_code=current_code,
        prompt_version=prompt_version,
        output_format=REVIEW_RESPONSE_SCHEMA,
    )

    response = generate_review(
        prompt=prompt,
        model=model,
    )

    return parse_review_response(response)