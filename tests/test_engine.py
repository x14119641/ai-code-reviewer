from pathlib import Path

import pytest

from reviewer.engine import (
    ReviewResult,
    build_changed_files_context,
    find_python_files,
    merge_specialized_reviews,
    review_diff,
    review_file,
    review_folder,
)
from reviewer.models import CodeReview, Issue
from reviewer.prompts import DEFAULT_PROMPT_VERSION


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

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        assert "print('hello')" in prompt
        assert model == "test-model"
        assert context_size == 4096

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
                severity="critical",
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

    def fake_llm(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        calls["prompt"] = prompt
        calls["model"] = model
        calls["context_size"] = str(context_size)

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
        "context_size": "4096",
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
        context_size: int = 4096,
    ) -> CodeReview:
        assert model == "test-model"
        assert prompt_version == DEFAULT_PROMPT_VERSION
        assert context_size == 4096
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


def test_build_changed_files_context_reads_python_files(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.py"
    second = tmp_path / "second.py"

    first.write_text(
        "value = 1\n",
        encoding="utf-8",
    )
    second.write_text(
        "print('hello')\n",
        encoding="utf-8",
    )

    result = build_changed_files_context([first, second])

    assert f"File: {first}" in result
    assert "value = 1" in result
    assert f"File: {second}" in result
    assert "print('hello')" in result


def test_build_changed_files_context_skips_missing_files(
    tmp_path: Path,
) -> None:
    existing = tmp_path / "existing.py"
    missing = tmp_path / "missing.py"

    existing.write_text(
        "value = 1\n",
        encoding="utf-8",
    )

    result = build_changed_files_context([existing, missing])

    assert f"File: {existing}" in result
    assert "value = 1" in result
    assert str(missing) not in result


def test_review_diff_includes_diff_and_current_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    diff = "-users: dict[str, int]\n+users: list[str]"
    current_code = """
def find_users(users: list[str]) -> None:
    for user in users:
        if user in users:
            pass
"""

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        assert diff in prompt
        assert current_code in prompt
        assert model == "test-model"
        assert context_size == 4096

        return '{"issues": []}'

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_diff(
        diff=diff,
        current_code=current_code,
        model="test-model",
        prompt_version="v8",
    )

    assert result.issues == []


def test_merge_specialized_reviews_uses_specialist_for_maintainability() -> None:
    general_review = CodeReview(
        issues=[
            Issue(
                severity="high",
                category="security",
                rule="sql_injection",
                title="SQL injection",
                explanation="Unsafe SQL construction.",
                recommendation="Use parameters.",
            ),
            Issue(
                severity="low",
                category="maintainability",
                rule="duplicate_code",
                title="General duplicate",
                explanation="General reviewer finding.",
                recommendation="Extract helper.",
            ),
        ]
    )

    maintainability_review = CodeReview(
        issues=[
            Issue(
                severity="low",
                category="maintainability",
                rule="duplicate_code",
                title="Specialist duplicate",
                explanation="Specialist reviewer finding.",
                recommendation="Extract helper.",
            )
        ]
    )

    merged = merge_specialized_reviews(
        general_review=general_review,
        maintainability_review=maintainability_review,
    )

    assert len(merged.issues) == 2

    assert merged.issues[0].rule == "sql_injection"
    assert merged.issues[1].rule == "duplicate_code"
    assert merged.issues[1].title == "Specialist duplicate"


def test_review_file_normalizes_resource_leak_severity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text(
        'file = open("data.txt")\n',
        encoding="utf-8",
    )

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        return """
        {
          "issues": [
            {
              "severity": "low",
              "category": "bug",
              "rule": "resource_leak",
              "title": "Resource is not closed",
              "explanation": "The opened resource is not reliably released.",
              "recommendation": "Use a context manager."
            }
          ]
        }
        """

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_file(
        path=source_file,
        model="test-model",
    )

    assert result == CodeReview(
        issues=[
            Issue(
                severity="medium",
                category="bug",
                rule="resource_leak",
                title="Resource is not closed",
                explanation="The opened resource is not reliably released.",
                recommendation="Use a context manager.",
            )
        ]
    )


def test_review_file_normalizes_broad_exception_handler_severity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text(
        "try:\n    process()\nexcept Exception:\n    pass\n",
        encoding="utf-8",
    )

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        return """
        {
          "issues": [
            {
              "severity": "low",
              "category": "bug",
              "rule": "broad_exception_handler",
              "title": "Broad exception is swallowed",
              "explanation": "Unexpected failures can be silently suppressed.",
              "recommendation": "Catch expected exceptions or re-raise unexpected failures."
            }
          ]
        }
        """

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_file(
        path=source_file,
        model="test-model",
    )

    assert result == CodeReview(
        issues=[
            Issue(
                severity="medium",
                category="bug",
                rule="broad_exception_handler",
                title="Broad exception is swallowed",
                explanation="Unexpected failures can be silently suppressed.",
                recommendation="Catch expected exceptions or re-raise unexpected failures.",
            )
        ]
    )


def test_review_file_normalizes_unsafe_deserialization_severity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text(
        "import pickle\n\nvalue = pickle.loads(payload)\n",
        encoding="utf-8",
    )

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        return """
        {
          "issues": [
            {
              "severity": "low",
              "category": "security",
              "rule": "unsafe_deserialization",
              "title": "Unsafe deserialization",
              "explanation": "Untrusted data is deserialized with pickle.",
              "recommendation": "Use a safe serialization format."
            }
          ]
        }
        """

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_file(
        path=source_file,
        model="test-model",
    )

    assert result == CodeReview(
        issues=[
            Issue(
                severity="high",
                category="security",
                rule="unsafe_deserialization",
                title="Unsafe deserialization",
                explanation="Untrusted data is deserialized with pickle.",
                recommendation="Use a safe serialization format.",
            )
        ]
    )
    
def test_review_file_normalizes_hardcoded_secret_severity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_file = tmp_path / "example.py"
    source_file.write_text(
        'API_KEY = "sk_live_example_123456"\n',
        encoding="utf-8",
    )

    def fake_generate_review(
        prompt: str,
        model: str,
        *,
        context_size: int = 4096,
    ) -> str:
        return """
        {
          "issues": [
            {
              "severity": "low",
              "category": "security",
              "rule": "hardcoded_secret",
              "title": "Hardcoded secret",
              "explanation": "A credential is embedded directly in source code.",
              "recommendation": "Load the credential from a secure external source."
            }
          ]
        }
        """

    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review,
    )

    result = review_file(
        path=source_file,
        model="test-model",
    )

    assert result == CodeReview(
        issues=[
            Issue(
                severity="high",
                category="security",
                rule="hardcoded_secret",
                title="Hardcoded secret",
                explanation="A credential is embedded directly in source code.",
                recommendation="Load the credential from a secure external source.",
            )
        ]
    )