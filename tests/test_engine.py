from pathlib import Path
import pytest

from reviewer.engine import review_file


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
    source_file.write_text("print('hello')", encoding="utf-")
    
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