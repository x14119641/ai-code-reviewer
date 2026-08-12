from subprocess import CalledProcessError, CompletedProcess
from unittest.mock import patch

import pytest

from reviewer.git_diff import GitDiffError, get_git_diff


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
