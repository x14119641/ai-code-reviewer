import subprocess


class GitDiffError(RuntimeError):
    """Raised when a Git diff cannot be obtained."""


def get_git_diff() -> str:
    """Return the current unstaged git diff."""
    try:
        result = subprocess.run(["git", "diff"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or "Could not obtain Git diff."
        raise GitDiffError(message) from exc
    return result.stdout
