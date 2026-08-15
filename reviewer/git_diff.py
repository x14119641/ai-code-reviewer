import subprocess
from pathlib import Path


class GitDiffError(RuntimeError):
    """Raised when a Git diff cannot be obtained."""


def get_git_diff() -> str:
    """Return the current unstaged git diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=10"], capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "Could not obtain Git diff."
        raise GitDiffError(message) from exc
    return result.stdout


def get_changed_python_files() -> list[Path]:
    """Return Python files changed in the current unstaged diff."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "--", "*.py"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "Could not obtain changed files."
        raise GitDiffError(message) from exc
    return [Path(line) for line in result.stdout.splitlines() if line.strip()]


def get_git_diff_against(base: str) -> str:
    """Return the diff between a base ref and HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", "--unified=10", f"{base}...HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or f"Could not obtain Git diff against {base}."
        raise GitDiffError(message) from exc

    return result.stdout


def get_changed_python_files_against(base: str) -> list[Path]:
    """Return Python files changed between a base ref and HEAD."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", f"{base}...HEAD", "--", "*.py"],
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = (
            exc.stderr.strip() or f"Could not obtain changed files against {base}."
        )
        raise GitDiffError(message) from exc

    return [Path(line) for line in result.stdout.splitlines() if line.strip()]
