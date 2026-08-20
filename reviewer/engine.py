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
    build_diff_verifier_prompt,
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
SPECIALIST_MAINTAINABILITY_RULES = {
    "duplicate_code",
    "long_function",
    "excessive_nesting",
}

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
    context_size: int = 4096,
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

    response = generate_review(prompt=prompt, model=model, context_size=context_size,)

    return parse_review_response(response)


def review_folder(path: Path, model: str, context_size: int = 4096,) -> Iterator[ReviewResult]:
    """Review all Python files found in a directory."""
    files = find_python_files(path=path)

    yield from review_files(files, model,context_size=context_size,)


def review_files(
    files: Iterable[Path],
    model: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    context_size: int = 4096,
) -> Iterator[ReviewResult]:
    """Review an iterable of Python files one at a time."""
    for file in files:
        review = review_file(file, model, prompt_version=prompt_version, context_size=context_size,)
        yield ReviewResult(path=file, review=review)


def review_diff(
    diff: str,
    current_code: str,
    model: str,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    context_size: int = 4096,
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
        context_size=context_size,
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
    context_size: int = 4096,
) -> CodeReview:
    """Find candidate issues in a Git diff for later verification."""
    prompt = build_diff_candidates_prompt(
        diff=diff,
        current_code=current_code,
        prompt_version=prompt_version,
    )

    response = generate_review(
        prompt=prompt,
        model=model,
        output_format=REVIEW_RESPONSE_SCHEMA,
        context_size=context_size,
    )

    return parse_review_response(response)


def serialize_review(review: CodeReview) -> str:
    return json.dumps(
        {
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "rule": issue.rule,
                    "title": issue.title,
                    "explanation": issue.explanation,
                    "recommendation": issue.recommendation,
                }
                for issue in review.issues
            ]
        },
        indent=2,
    )


def verify_diff_candidates(
    diff: str,
    current_code: str,
    candidates: CodeReview,
    model: str,
    prompt_version: str,
    context_size: int = 4096,
) -> CodeReview:
    """Verify candidate issues against the diff and current code."""
    candidates_json = serialize_review(candidates)

    prompt = build_diff_verifier_prompt(
        diff=diff,
        current_code=current_code,
        candidates=candidates_json,
        prompt_version=prompt_version,
    )

    response = generate_review(
        prompt=prompt,
        model=model,
        output_format=REVIEW_RESPONSE_SCHEMA,
        context_size=context_size,
    )

    return parse_review_response(response)


def review_diff_multi_pass(
    diff: str,
    current_code: str,
    model: str,
    prompt_version: str,
    context_size: int = 4096,
) -> CodeReview:
    """Review a Git diff using candidate generation followed by verification."""
    candidates = find_diff_candidates(
        diff=diff,
        current_code=current_code,
        model=model,
        prompt_version=prompt_version,
        context_size=context_size,
    )

    return verify_diff_candidates(
        diff=diff,
        current_code=current_code,
        candidates=candidates,
        model=model,
        prompt_version=prompt_version,
        context_size=context_size,
    )


def merge_specialized_reviews(
    general_review: CodeReview,
    maintainability_review: CodeReview,
) -> CodeReview:
    """Merge general and specialist reviews using deterministic rule ownership."""

    general_issues = [
        issue
        for issue in general_review.issues
        if issue.rule not in SPECIALIST_MAINTAINABILITY_RULES
    ]

    maintainability_issues = [
        issue
        for issue in maintainability_review.issues
        if issue.rule in SPECIALIST_MAINTAINABILITY_RULES
    ]

    return CodeReview(
        issues=[
            *general_issues,
            *maintainability_issues,
        ]
    )
    

def review_diff_specialized(
    diff: str,
    current_code: str,
    model: str,
    general_prompt_version: str = "v11",
    maintainability_prompt_version: str = "maintainability_v1",
    context_size: int = 4096,
) -> CodeReview:
    """Review a Git diff using general and maintainability-specialist passes."""

    general_review = review_diff(
        diff=diff,
        current_code=current_code,
        model=model,
        prompt_version=general_prompt_version,
        context_size=context_size,
    )

    maintainability_review = find_diff_candidates(
        diff=diff,
        current_code=current_code,
        model=model,
        prompt_version=maintainability_prompt_version,
        context_size=context_size,
    )

    return merge_specialized_reviews(
        general_review=general_review,
        maintainability_review=maintainability_review,
    )
    

def review_file_specialized(
    path: Path,
    model: str,
    general_prompt_version: str = "v5",
    maintainability_prompt_version: str = "maintainability_file_v1",
    context_size: int = 4096,
) -> CodeReview:
    """Review one file using general and maintainability-specialist passes."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    code = path.read_text(encoding="utf-8")

    general_prompt = build_review_prompt(
        code,
        prompt_version=general_prompt_version,
    )

    general_response = generate_review(
        prompt=general_prompt,
        model=model,
        context_size=context_size,
    )

    general_review = parse_review_response(general_response)

    specialist_prompt = build_review_prompt(
        code,
        prompt_version=maintainability_prompt_version,
    )

    specialist_response = generate_review(
        prompt=specialist_prompt,
        model=model,
        output_format=REVIEW_RESPONSE_SCHEMA,
        context_size=context_size,
    )

    maintainability_review = parse_review_response(specialist_response)

    return merge_specialized_reviews(
        general_review=general_review,
        maintainability_review=maintainability_review,
    )