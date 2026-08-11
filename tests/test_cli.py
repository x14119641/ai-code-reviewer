from pathlib import Path

from rich.console import Console
from typer.testing import CliRunner

import main
from reviewer import rendering
from reviewer.prompts import DEFAULT_PROMPT_VERSION
from tests.test_result_comparison import write_result

runner = CliRunner()


def test_compare_results_displays_models(
    tmp_path: Path,
    monkeypatch,
) -> None:
    write_result(
        tmp_path / "first.json",
        model="qwen3.5:9b",
        accuracy=0.857,
        prompt_version=DEFAULT_PROMPT_VERSION,
    )
    write_result(
        tmp_path / "second.json",
        model="qwen2.5-coder:7b",
        accuracy=0.8,
        prompt_version=DEFAULT_PROMPT_VERSION,
    )

    monkeypatch.setattr(
        rendering,
        "console",
        Console(width=160),
    )

    result = runner.invoke(
        main.app,
        ["compare-results", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "qwen3.5:9b" in result.stdout
    assert "qwen2.5-coder:7b" in result.stdout
    assert DEFAULT_PROMPT_VERSION in result.stdout
    assert "85.7%" in result.stdout
    assert "80.0%" in result.stdout


def test_compare_results_rejects_rule_and_category_together() -> None:
    result = runner.invoke(
        main.app,
        [
            "compare-results",
            "results/",
            "--by-rule",
            "--by-category",
        ],
    )

    assert result.exit_code == 1
    assert "Use either --by-rule or --by-category, not both." in result.stdout


def test_compare_results_rejects_missing_directory(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "does-not-exist"

    result = runner.invoke(
        main.app,
        ["compare-results", str(missing)],
    )

    assert result.exit_code == 1
    assert "Results directory does not exist" in result.stdout


def test_analyze_result_rejects_missing_file(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing.json"

    result = runner.invoke(
        main.app,
        ["analyze-result", str(missing)],
    )

    assert result.exit_code == 1
    assert "Could not read result file" in result.stdout
