from pathlib import Path
import pytest

from reviewer.engine import find_python_files, review_file


def test_review_file_raises_when_file_does_not_exists(tmp_path:Path) -> None:
    missing_file = tmp_path / "missing.py"
    with pytest.raises(FileNotFoundError, match="File not found"):
        review_file(path=missing_file, model="test-model")
        
        
def test_review_file_raises_when_path_is_directory(tmp_path:Path) -> None:
    directory = tmp_path / "project_missing"
    directory.mkdir()
    with pytest.raises(ValueError, match="Not a file"):
        review_file(path=directory, model="test-model")
        

def test_review_file_return_model_response(tmp_path:Path, monkeypatch:pytest.MonkeyPatch,) -> None:
    source_file = tmp_path/ "example.py"
    source_file.write_text("print('hello')", encoding="utf-8")
    
    def fake_generate_review(prompt:str, model:str) ->str:
        assert "print('hello')" in prompt
        assert model == "test-model"
        return "Fake review result"
    
    monkeypatch.setattr(
        "reviewer.engine.generate_review",
        fake_generate_review
    )
    
    result = review_file(path=source_file, model="test-model")
    
    assert result ==  "Fake review result"
    


def test_review_file_builds_prompt_and_calls_llm(tmp_path:Path, monkeypatch: pytest.MonkeyPatch) ->None:
    source_file = tmp_path/ "example.py"
    source_file.write_text("print('hello')", encoding="utf-8")
    
    calls = {}
    
    def fake_prompt(code:str)-> str:
        calls["code"] = code
        return ("PROMPT")
    
    def fake_llm(prompt:str, model:str) -> str:
        calls["prompt"] = prompt
        calls["model"] = model
        return "RESULT"
    
    monkeypatch.setattr(
        "reviewer.engine.build_review_prompt",
        fake_prompt,
    )
    
    monkeypatch.setattr(
            "reviewer.engine.generate_review",
            fake_llm,
        )
    
    result = review_file(source_file, "test-model")
    
    assert result == "RESULT"
    assert calls == {
        "code": "print('hello')",
        "prompt": "PROMPT",
        "model": "test-model"
    }
    
    
def test_find_python_files_finds_python_files_recursively(tmp_path:Path) -> None:
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