from pathlib import Path

import typer
from rich.console import Console

from reviewer.prompts import DEFAULT_PROMPT_VERSION
from reviewer.benchmark_serialization import save_benchmark_run
from reviewer.engine import review_file, review_files, find_python_files
from reviewer.benchmark_runner import find_benchmark_files, run_benchmarks
from reviewer.rendering import (
    build_category_comparison_table,
    build_comparison_table,
    build_rule_comparison_table,
    print_benchmark_evaluations,
    print_benchmark_failures,
    print_benchmark_progress,
    print_benchmark_summary,
    print_result_analysis,
    print_result_saved,
    print_review,
)
from reviewer.result_comparison import (
    ResultComparisonError,
    load_result,
    load_result_summaries,
    load_results,
)
from reviewer.models import CodeReview

app = typer.Typer()
console = Console()


@app.callback()
def main() -> None:
    """Local AI-powered code reviewer."""


@app.command("review")
def review_command(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review a single Python file."""
    try:
        result = review_file(path=path, model=model)
        print_review(review=result)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Could not read the file:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command("review-folder")
def review_folder_command(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review all Python files in a folder."""
    try:
        files = find_python_files(path)
        total = len(files)
        if total == 0:
            console.print("[yellow]No Python files found.[/yellow]")
            return

        for i, result in enumerate(review_files(files, model), start=1):
            console.rule(f"[cyan]Reviewing {i}/{total}[/cyan] -> {result.path}")
            if result.error:
                console.print(f"[red]{result.error}[/red]")
                continue
            print_review(result.review)
        console.print(f"\n[green]✓ Reviewed {total} Python files.[/green]")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Review Failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command("benchmark")
def benchmark_command(
    path: Path,
    model: str = typer.Option(
        "qwen3.5:9b",
        help="Ollama model used for the benchmark",
    ),
    output: Path | None = typer.Option(
        None,
        help="Output filename or path.",
    ),
    prompt_version: str = typer.Option(
        DEFAULT_PROMPT_VERSION,
        "--prompt-version",
        help="Prompt version used for the benchmark.",
    ),
) -> None:
    """Evaluate the AI reviewer using benchmark cases."""

    try:
        benchmark_paths = find_benchmark_files(path)

        if not benchmark_paths:
            console.print(
                "[yellow]No benchmark files found.[/yellow]"
            )
            return

        total = len(benchmark_paths)
        current = 0

        def review_with_model(
            source_path: Path,
        ) -> CodeReview:
            nonlocal current

            current += 1

            print_benchmark_progress(
                current=current,
                total=total,
                path=source_path,
            )

            return review_file(
                source_path,
                model,
                prompt_version=prompt_version,
            )

        run = run_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
            prompt_version=prompt_version,
        )

        if output is not None:
            if output.parent == Path("."):
                output = (
                    Path("results")
                    / prompt_version
                    / output
                )

            save_benchmark_run(run, output)
            print_result_saved(output)

        print_benchmark_evaluations(run)
        print_benchmark_failures(run)
        print_benchmark_summary(run)

    except (
        FileNotFoundError,
        ValueError,
        RuntimeError,
    ) as exc:
        console.print(
            f"[red]Benchmark Failed:[/red] {exc}"
        )
        raise typer.Exit(code=1) from exc


@app.command("compare-results")
def compare_results(
    directory: Path,
    by_rule: bool = typer.Option(
        False, "--by-rule", help="Compare benchmark results grouped by rule"
    ),
    by_category: bool = typer.Option(
        False, "--by-category", help="Compare benchmark results grouped by category"
    ),
) -> None:
    """Compare previously exported benchmark result files"""
    if by_rule and by_category:
        console.print(
            "[red]Error:[/red] Use either --by-rule " "or --by-category, not both."
        )
        raise typer.Exit(code=1)
    try:
        if by_rule:
            results = load_results(directory)

            results.sort(
                key=lambda result: result.summary.accuracy,
                reverse=True,
            )

            table = build_rule_comparison_table(results)
        elif by_category:
            results = load_results(directory)

            results.sort(
                key=lambda result: result.summary.accuracy,
                reverse=True,
            )

            table = build_category_comparison_table(results)
        else:
            summaries = load_result_summaries(directory)

            summaries.sort(
                key=lambda summary: summary.accuracy,
                reverse=True,
            )

            table = build_comparison_table(summaries)

    except ResultComparisonError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error

    console.print(table)


@app.command("analyze-result")
def analyze_result_command(
    path: Path = typer.Argument(
        ...,
        help="Path to an exported benchmark result JSON file.",
    ),
) -> None:
    """Show detection failures and severity mismatches."""

    try:
        result = load_result(path)
        print_result_analysis(result)
    except ResultComparisonError as error:
        console.print(f"[red]Error:[/red] {error}")
        raise typer.Exit(code=1) from error


if __name__ == "__main__":
    app()
