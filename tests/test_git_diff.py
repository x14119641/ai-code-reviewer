from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest.mock import patch

import pytest

from reviewer.git_diff import GitDiffError, get_changed_python_files, get_git_diff


def test_get_git_diff_returns_diff() -> None:
    diff = """
        diff --git a/example.py b/example.py
        --- a/example.py
        +++ b/example.py
        @@ -1 +1 @@
        -old = 1
        +new = 2
    """

    with patch(
        "reviewer.git_diff.subprocess.run",
        return_value=CompletedProcess(
            args=["git", "diff"],
            returncode=0,
            stdout=diff,
            stderr="",
        ),
    ):
        result = get_git_diff()

    assert result == diff


def test_get_git_diff_raises_error_when_git_fails() -> None:
    error = CalledProcessError(
        returncode=128,
        cmd=["git", "diff"],
        stderr="fatal: not a git repository",
    )

    with (
        patch("reviewer.git_diff.subprocess.run", side_effect=error),
        pytest.raises(GitDiffError, match="not a git repository"),
    ):
        get_git_diff()


def test_get_changed_python_files_returns_paths() -> None:
    output = """\
reviewer/git_diff.py
reviewer/engine.py
"""

    with patch(
        "reviewer.git_diff.subprocess.run",
        return_value=CompletedProcess(
            args=["git", "diff", "--name-only", "--", "*.py"],
            returncode=0,
            stdout=output,
            stderr="",
        ),
    ):
        result = get_changed_python_files()

    assert result == [
        Path("reviewer/git_diff.py"),
        Path("reviewer/engine.py"),
    ]


def test_get_changed_python_files_raises_error() -> None:
    error = CalledProcessError(
        returncode=128,
        cmd=["git", "diff", "--name-only", "--", "*.py"],
        stderr="fatal: Could not obtain changed files",
    )

    with (
        patch("reviewer.git_diff.subprocess.run", side_effect=error),
        pytest.raises(GitDiffError, match="Could not obtain changed files"),
    ):
        get_changed_python_files()
