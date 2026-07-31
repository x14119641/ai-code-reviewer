from pathlib import Path
import json
import pytest

from reviewer.benchmarks import BenchmarkLoadError, load_benchmark


def write_benchmark_files(
    directory: Path, *, code:str, definition: object, filename:str="example"
) -> Path:
    code_path = directory / f"{filename}.py"
    definition_path = directory / f"{filename}.json"
    code_path.write_text(code, encoding="utf-8")
    definition_path.write_text(
        json.dumps(definition),
        encoding="utf-8",
    )

    return code_path


def test_load_benchmark_with_expected_issue(tmp_path:Path) ->None:
    code_path = write_benchmark_files(
        tmp_path,
        code="def find_user(name):\n    return name\n",
        definition={
            "name": "Example security benchmark",
            "expected_issues": [
                {
                    "category": "security",
                    "rule": "sql_injection",
                    "severity": "high",
                    "explanation": "User input is not validated.",
                }
            ],
        },
    )
    
    benchmark = load_benchmark(code_path=code_path)
    
    assert benchmark.name == "Example security benchmark"
    assert benchmark.source_code.startswith("def find_user")
    assert benchmark.expects_issues is True
    assert len(benchmark.expected_issues) == 1

    expected_issue = benchmark.expected_issues[0]

    assert expected_issue.category == "security"
    assert expected_issue.severity == "high"
    assert expected_issue.explanation == (
        "User input is not validated."
    )
    
    
def test_load_clean_benchmark(tmp_path: Path) -> None:
    code_path = write_benchmark_files(
        tmp_path,
        code="def add(left, right):\n    return left + right\n",
        definition={
            "name": "Clean addition function",
            "expected_issues": [],
        },
    )

    benchmark = load_benchmark(code_path)

    assert benchmark.expects_issues is False
    assert benchmark.expected_issues == ()
    

def test_load_benchmark_requires_matching_json(
    tmp_path: Path,
) -> None:
    code_path = tmp_path / "missing_definition.py"
    code_path.write_text("value = 1\n", encoding="utf-8")

    with pytest.raises(
        BenchmarkLoadError,
        match="Benchmark definition does not exist",
    ):
        load_benchmark(code_path)
        

def test_load_benchmark_rejects_invalid_json(
    tmp_path: Path,
) -> None:
    code_path = tmp_path / "invalid.py"
    definition_path = tmp_path / "invalid.json"

    code_path.write_text("value = 1\n", encoding="utf-8")
    definition_path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(
        BenchmarkLoadError,
        match="Invalid JSON",
    ):
        load_benchmark(code_path)
        
    
def test_load_benchmark_rejects_invalid_severity(
    tmp_path: Path,
) -> None:
    code_path = write_benchmark_files(
        tmp_path,
        code="value = 1\n",
        definition={
            "name": "Invalid severity benchmark",
            "expected_issues": [
                {
                    "category": "bug",
                    "rule": "sql_injection",
                    "severity": "extreme",
                    "explanation": "Example issue.",
                }
            ],
        },
    )

    with pytest.raises(
        BenchmarkLoadError,
        match="invalid severity",
    ):
        load_benchmark(code_path)


def test_load_benchmark_rejects_missing_name(
    tmp_path: Path,
) -> None:
    code_path = write_benchmark_files(
        tmp_path,
        code="value = 1\n",
        definition={
            "expected_issues": [],
        },
    )

    with pytest.raises(
        BenchmarkLoadError,
        match="'name'",
    ):
        load_benchmark(code_path)