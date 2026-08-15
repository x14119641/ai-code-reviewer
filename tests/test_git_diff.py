from pathlib import Path
from subprocess import CalledProcessError, CompletedProcess
from unittest.mock import patch

import pytest

from reviewer.git_diff import (
    GitDiffError,
    get_changed_python_files,
    get_changed_python_files_against,
    get_git_diff,
    get_git_diff_against,
)


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


def test_get_git_diff_against_returns_diff() -> None:
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
            args=["git", "diff", "--unified=10", "main...HEAD"],
            returncode=0,
            stdout=diff,
            stderr="",
        ),
    ) as run_mock:
        result = get_git_diff_against("main")

    assert result == diff

    run_mock.assert_called_once_with(
        ["git", "diff", "--unified=10", "main...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )


def test_get_git_diff_against_raises_error_when_git_fails() -> None:
    error = CalledProcessError(
        returncode=128,
        cmd=["git", "diff", "--unified=10", "missing...HEAD"],
        stderr="fatal: ambiguous argument 'missing...HEAD'",
    )

    with (
        patch("reviewer.git_diff.subprocess.run", side_effect=error),
        pytest.raises(GitDiffError, match="ambiguous argument"),
    ):
        get_git_diff_against("missing")


def test_get_changed_python_files_against_returns_paths() -> None:
    output = """\
reviewer/git_diff.py
reviewer/engine.py
"""

    with patch(
        "reviewer.git_diff.subprocess.run",
        return_value=CompletedProcess(
            args=[
                "git",
                "diff",
                "--name-only",
                "main...HEAD",
                "--",
                "*.py",
            ],
            returncode=0,
            stdout=output,
            stderr="",
        ),
    ) as run_mock:
        result = get_changed_python_files_against("main")

    assert result == [
        Path("reviewer/git_diff.py"),
        Path("reviewer/engine.py"),
    ]

    run_mock.assert_called_once_with(
        [
            "git",
            "diff",
            "--name-only",
            "main...HEAD",
            "--",
            "*.py",
        ],
        capture_output=True,
        text=True,
        check=True,
    )


def test_get_changed_python_files_against_raises_error() -> None:
    error = CalledProcessError(
        returncode=128,
        cmd=[
            "git",
            "diff",
            "--name-only",
            "missing...HEAD",
            "--",
            "*.py",
        ],
        stderr="fatal: ambiguous argument 'missing...HEAD'",
    )

    with (
        patch("reviewer.git_diff.subprocess.run", side_effect=error),
        pytest.raises(GitDiffError, match="ambiguous argument"),
    ):
        get_changed_python_files_against("missing")