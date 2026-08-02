from pathlib import Path
from reviewer.prompts import DEFAULT_PROMPT_VERSION

import pytest

from reviewer.engine import (
    ReviewResult,
    find_python_files,
    review_file,
    review_folder,
)
from reviewer.models import CodeReview, Issue


def test_review_file_raises_when_file_does_not_exist(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.py"

    with pytest.raises(FileNotFoundError, match="File not found"):
        review_file(path=missing_file, model="test-model")


def test_review_file_raises_when_path_is_directory(tmp_path: Path) -> None:
    directory = tmp_path / "project_missing"
    directory.mkdir()

    with pytest.raises(ValueError, match="Not a file"):
        review_file(path=directory, model="test-model")


def test_review_file_returns_parsed_code_review(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text("print('hello')", encoding="utf-8")

    def fake_generate_review(prompt: str, model: str) -> str:
        assert "print('hello')" in prompt
        assert model == "test-model"

        return """
        {
          "issues": [
            {
              "severity": "high",
              "category": "security",
              "rule": "sql_injection",
              "title": "Fake issue",
              "explanation": "Fake explanation.",
              "recommendation": "Fake recommendation."
            }
          ]
        }
        """

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_file(path=source_file, model="test-model")

    assert result == CodeReview(
        issues=[
            Issue(
                severity="high",
                category="security",
                rule="sql_injection",
                title="Fake issue",
                explanation="Fake explanation.",
                recommendation="Fake recommendation.",
            )
        ]
    )


def test_review_file_builds_prompt_and_calls_llm(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text("print('hello')", encoding="utf-8")

    calls: dict[str, str] = {}

    def fake_prompt(
        source_code: str,
        prompt_version: str = DEFAULT_PROMPT_VERSION,
    ) -> str:
        calls["code"] = source_code
        calls["prompt_version"] = prompt_version

        return f"PROMPT:{source_code}"

    def fake_llm(prompt: str, model: str) -> str:
        calls["prompt"] = prompt
        calls["model"] = model

        return '{"issues": []}'

    monkeypatch.setattr(
        "reviewer.engine.build_review_prompt",
        fake_prompt,
    )
    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_llm,
    )

    result = review_file(
        source_file,
        "test-model",
        prompt_version="v1",
    )

    assert result == CodeReview(issues=[])

    assert calls == {
        "code": "print('hello')",
        "prompt_version": "v1",
        "prompt": "PROMPT:print('hello')",
        "model": "test-model",
    }


def test_find_python_files_finds_python_files_recursively(
    tmp_path: Path,
) -> None:
    root_file = tmp_path / "main.py"
    root_file.write_text("", encoding="utf-8")

    package = tmp_path / "package"
    package.mkdir()

    nested_file = package / "service.py"
    nested_file.write_text("", encoding="utf-8")

    result = find_python_files(tmp_path)

    assert result == [root_file, nested_file]


def test_find_python_files_ignores_excluded_directories(
    tmp_path: Path,
) -> None:
    valid_file = tmp_path / "main.py"
    valid_file.write_text("", encoding="utf-8")

    for directory_name in (".git", ".venv", "__pycache__"):
        directory = tmp_path / directory_name
        directory.mkdir()

        ignored_file = directory / "ignored.py"
        ignored_file.write_text("", encoding="utf-8")

    result = find_python_files(tmp_path)

    assert result == [valid_file]


def test_find_python_files_ignores_non_python_files(
    tmp_path: Path,
) -> None:
    python_file = tmp_path / "main.py"
    python_file.write_text("", encoding="utf-8")

    text_file = tmp_path / "notes.txt"
    text_file.write_text("", encoding="utf-8")

    result = find_python_files(tmp_path)

    assert result == [python_file]


def test_find_python_files_raises_when_directory_does_not_exist(
    tmp_path: Path,
) -> None:
    missing_directory = tmp_path / "missing"

    with pytest.raises(FileNotFoundError, match="Path not found"):
        find_python_files(missing_directory)


def test_find_python_files_raises_when_path_is_file(
    tmp_path: Path,
) -> None:
    file = tmp_path / "example.py"
    file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Not a directory"):
        find_python_files(file)


def test_review_folder_reviews_all_python_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first_file = tmp_path / "first.py"
    first_file.write_text("", encoding="utf-8")

    package = tmp_path / "package"
    package.mkdir()

    second_file = package / "second.py"
    second_file.write_text("", encoding="utf-8")

    fake_review = CodeReview(
        issues=[
            Issue(
                severity="medium",
                category="security",
                rule="sql_injection",
                title="Test issue",
                explanation="Test explanation.",
                recommendation="Test recommendation.",
            )
        ]
    )

    def fake_review_file(
        path: Path,
        model: str,
        prompt_version: str = DEFAULT_PROMPT_VERSION,
    ) -> CodeReview:
        assert model == "test-model"
        assert prompt_version == DEFAULT_PROMPT_VERSION
        return fake_review

    monkeypatch.setattr(
        "reviewer.engine.review_file",
        fake_review_file,
    )

    result = list(
        review_folder(
            path=tmp_path,
            model="test-model",
        )
    )

    assert result == [
        ReviewResult(
            path=first_file,
            review=fake_review,
        ),
        ReviewResult(
            path=second_file,
            review=fake_review,
        ),
    ]


def test_review_folder_returns_no_results_for_empty_directory(
    tmp_path: Path,
) -> None:
    result = list(
        review_folder(
            path=tmp_path,
            model="test-model",
        )
    )

    assert result == []
