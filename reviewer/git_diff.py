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
    """Return the name files changed."""
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
