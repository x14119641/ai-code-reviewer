from pathlib import Path

import typer
from rich.console import Console


from reviewer.benchmark_serialization import save_benchmark_run
from reviewer.engine import review_file, review_files, find_python_files
from reviewer.benchmark_runner import find_benchmark_files, run_benchmarks
from reviewer.rendering import (
    build_category_comparison_table,
    build_comparison_table,
    build_rule_comparison_table,
    print_review,
)
from reviewer.result_comparison import (
    ResultComparisonError,
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
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the benchmark"),
    output: Path | None = typer.Option(None, help="Output filename or path."),
) -> None:
    """Evaluate the AI reviewer using benchmark cases."""
    try:
        benchmark_paths = find_benchmark_files(path)

        if not benchmark_paths:
            console.print("[yellow]No benchmark files found.[/yellow]")
            return
        total = len(benchmark_paths)
        current = 0

        def review_with_model(source_path: Path) -> CodeReview:
            nonlocal current
            current += 1
            console.rule(f"[cyan]Benchmark {current}/{total}[/cyan] -> {source_path}")
            return review_file(source_path, model)

        run = run_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model,
            model=model,
        )

        if output is not None:
            if output.parent == Path("."):
                output = Path("results") / output

            save_benchmark_run(run, output)
            console.print()
            console.print(f"[green]✓ Results saved to:[/green] {output}")

        console.print()
        console.rule("[bold]Individual results[/bold]")

        for evaluation in run.evaluations:
            benchmark_name = evaluation.benchmark.name
            file_name = evaluation.benchmark.code_path.name

            if evaluation.passed:
                console.print(
                    f"[bold green]PASS[/bold green] "
                    f"{benchmark_name} "
                    f"[dim]({file_name})[/dim]"
                )
                continue

            expected_rules = [
                issue.rule for issue in evaluation.benchmark.expected_issues
            ]

            actual_rules = [issue.rule for issue in evaluation.review.issues]

            console.print(
                f"[bold red]FAIL[/bold red] "
                f"{benchmark_name} "
                f"[dim]({file_name})[/dim]"
            )

            console.print(
                "  Expected: "
                f"{', '.join(expected_rules) if expected_rules else 'no issues'}"
            )

            console.print(
                "  Actual:   "
                f"{', '.join(actual_rules) if actual_rules else 'no issues'}"
            )

            if evaluation.false_positive:
                console.print("  Result: [red]False positive[/red]")
            elif evaluation.false_negative:
                console.print("  Result: [red]False negative[/red]")
            elif not evaluation.rule_matched:
                console.print("  Result: [red]Wrong rule[/red]")

        if run.failures:
            console.print()
            console.rule("[bold red]Execution faiulures[/bold red]")
            for failure in run.failures:
                console.print(
                    f"[bold red]ERROR[/bold red] "
                    f"{failure.benchmark.name} "
                    f"[dim]({failure.benchmark.code_path.name})[/dim]"
                )
                console.print(f"  Type:    {failure.error_type}")
                console.print(f"  Message: {failure.message}")
                console.print()

        console.print()
        console.rule("[bold green]Benchmark results[/bold green]")

        console.print(f"[bold]Model:[/bold] {model}")
        console.print(f"[bold]Benchmarks:[/bold] {run.benchmark_count}")
        console.print(f"[green]Passed:[/green] {run.passed}")
        console.print(f"[red]Failed:[/red] {run.failed}")
        console.print(f"[bold red]Response errors:[/bold red] {run.failure_count}")
        console.print(f"[yellow]False positives:[/yellow] {run.false_positives}")
        console.print(f"[yellow]False negatives:[/yellow] {run.false_negatives}")
        console.print(f"[bold cyan]Accuracy:[/bold cyan] {run.accuracy:.2%}")
        console.print(
            f"[bold purple4]Severity Count:[/bold purple4] {run.severity_evaluated_count}"
        )
        console.print(
            f"[bold purple4]Severity Matches:[/bold purple4] {run.severity_matches}"
        )
        console.print(
            f"[bold purple4]Severity Accuracy:[/bold purple4] {run.severity_accuracy:.2%}"
        )

        console.print(f"[bold cyan]Duration:[/bold cyan] {run.duration_seconds:.2f} s")

    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Benchmark Failed:[/red] {exc}")
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


if __name__ == "__main__":
    app()
