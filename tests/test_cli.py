from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console
from typer.testing import CliRunner

import main
from reviewer import rendering
from reviewer.models import BenchmarkRun
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


def test_benchmark_diff_runs_with_model_and_prompt_version(
    tmp_path: Path,
    monkeypatch,
) -> None:
    benchmark_path = tmp_path / "diff_case"
    benchmark_path.mkdir()

    discovered_paths = (benchmark_path,)

    received_model = None
    received_prompt_version = None
    received_paths = None

    def fake_find_diff_benchmarks(
        path: Path,
    ) -> tuple[Path, ...]:
        return discovered_paths

    def fake_run_diff_benchmarks(
        benchmark_paths,
        review_function,
        *,
        model: str,
        prompt_version: str,
    ) -> BenchmarkRun:
        nonlocal received_model
        nonlocal received_prompt_version
        nonlocal received_paths

        received_model = model
        received_prompt_version = prompt_version
        received_paths = benchmark_paths

        return BenchmarkRun(
            created_at=datetime.now(UTC),
            model=model,
            prompt_version=prompt_version,
            evaluations=(),
            duration_seconds=0.1,
        )

    monkeypatch.setattr(
        main,
        "find_diff_benchmarks",
        fake_find_diff_benchmarks,
    )

    monkeypatch.setattr(
        main,
        "run_diff_benchmarks",
        fake_run_diff_benchmarks,
    )

    result = runner.invoke(
        main.app,
        [
            "benchmark-diff",
            str(tmp_path),
            "--model",
            "test-model",
            "--prompt-version",
            "v9",
        ],
    )

    assert result.exit_code == 0
    assert received_paths == discovered_paths
    assert received_model == "test-model"
    assert received_prompt_version == "v9"
