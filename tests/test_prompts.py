from pathlib import Path

import pytest

from reviewer.prompts import build_diff_prompt, build_review_prompt


def test_build_review_prompt_inserts_source_code(
    tmp_path: Path,
    monkeypatch,
) -> None:
    prompts_directory = tmp_path / "prompts"
    version_directory = prompts_directory / "v1"
    version_directory.mkdir(parents=True)

    template_path = version_directory / "review.txt"
    template_path.write_text(
        "Review this code:\n{{SOURCE_CODE}}",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "reviewer.prompts.PROMPTS_DIRECTORY",
        prompts_directory,
    )

    prompt = build_review_prompt(
        "def add(a, b):\n    return a + b",
        prompt_version="v1",
    )

    assert "def add(a, b):" in prompt
    assert "{{SOURCE_CODE}}" not in prompt


def test_build_review_prompt_rejects_unknown_version(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        "reviewer.prompts.PROMPTS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="Prompt template not found",
    ):
        build_review_prompt(
            "value = 1",
            prompt_version="missing",
        )


def test_build_review_prompt_requires_source_placeholder(
    tmp_path: Path,
    monkeypatch,
) -> None:
    version_directory = tmp_path / "v1"
    version_directory.mkdir()

    (version_directory / "review.txt").write_text(
        "Review this code.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "reviewer.prompts.PROMPTS_DIRECTORY",
        tmp_path,
    )

    with pytest.raises(
        ValueError,
        match="missing",
    ):
        build_review_prompt(
            "value = 1",
            prompt_version="v1",
        )


def test_build_diff_prompt_replaces_diff_placeholder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts_dir = tmp_path / "prompts"
    version_dir = prompts_dir / "v1"
    version_dir.mkdir(parents=True)

    (version_dir / "diff.txt").write_text(
        "Review this diff:\n{{DIFF}}",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "reviewer.prompts.PROMPTS_DIRECTORY",
        prompts_dir,
    )

    result = build_diff_prompt(
        "+new_line = True",
        prompt_version="v1",
    )

    assert result == "Review this diff:\n+new_line = True"


def test_build_diff_prompt_raises_when_placeholder_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    prompts_dir = tmp_path / "prompts"
    version_dir = prompts_dir / "v1"
    version_dir.mkdir(parents=True)

    (version_dir / "diff.txt").write_text(
        "Review this diff",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "reviewer.prompts.PROMPTS_DIRECTORY",
        prompts_dir,
    )

    with pytest.raises(
        ValueError,
        match=r"\{\{DIFF\}\}",
    ):
        build_diff_prompt(
            "+new_line = True",
            prompt_version="v1",
        )
