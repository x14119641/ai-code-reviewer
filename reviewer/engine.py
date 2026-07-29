from pathlib import Path
from dataclasses import dataclass


from reviewer.llm import generate_review
from reviewer.prompts import build_review_prompt
from collections.abc import Iterable, Iterator

IGNORED_DIRECTORIES = {".git", ".venv", "__pycache__"}


@dataclass
class ReviewResult:
    path: Path
    review: str


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


def review_file(
    path: Path,
    model: str,
) -> None:
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

    return generate_review(prompt=prompt, model=model)


def review_folder(path: Path, model: str) -> Iterator[ReviewResult]:
    """Review all Python files found in a directory."""
    files = find_python_files(path=path)

    yield from review_files(files, model)


def review_files(files: Iterable[Path], model: str) -> Iterator[ReviewResult]:
    """Review an iterable of Python files one at a time."""
    for file in files:
        review = review_file(file, model)
        yield ReviewResult(path=file, review=review)
