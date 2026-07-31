from pathlib import Path

from typer.testing import CliRunner

from main import app

from tests.test_result_comparison import write_result


runner = CliRunner()


def test_compare_results_displays_models(
    tmp_path: Path,
) -> None:
    write_result(
        tmp_path / "first.json",
        model="qwen3.5:9b",
        accuracy=85.7,
    )
    write_result(
        tmp_path / "second.json",
        model="qwen2.5-coder:7b",
        accuracy=80.0,
    )

    result = runner.invoke(
        app,
        ["compare-results", str(tmp_path)],
    )

    assert result.exit_code == 0
    assert "qwen3.5:9b" in result.stdout
    assert "qwen2.5-coder:7b" in result.stdout
    assert "85.7%" in result.stdout
    assert "80.0%" in result.stdout