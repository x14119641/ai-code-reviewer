from pathlib import Path

import typer
from rich.console import Console

from reviewer.engine import review_file, review_files, find_python_files
from reviewer.benchmark_runner import find_benchmark_files, run_benchmarks
from reviewer.models import CodeReview

app = typer.Typer()
console = Console()


def print_review(review) -> None:
    if not review.issues:
        console.print("[green]No meaningful issues found.[/green]")
        return
    for issue in review.issues:
        console.print(f"[bold]{issue.title}[/bold]")
        console.print(f"[yellow]Severity:[/yellow] {issue.severity}")
        console.print(f"[cyan]Category:[/cyan] {issue.category}")
        console.print(issue.explanation)
        console.print(f"[green]Recommendation:[/green] {issue.recommendation}")
        console.print()


@app.callback()
def main() -> None:
    """Local AI-powered code reviewer."""


@app.command("review")
def review_command(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review a single Python file in a folder."""
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
    model: str=typer.Option("qwen3.5:9b", help="Ollama model used for the benchemark"),
) -> None:
    """Evaluate the AI reviewer using benchmark cases."""
    try:
        benchmark_paths = find_benchmark_files(path)
        
        if not benchmark_paths:
            console.print("[yellow]No benchmark files found.[/yellow]")
            return
        total = len(benchmark_paths)
        current = 0
        
        def review_with_model(source_path:Path) ->CodeReview:
            nonlocal current
            current +=1
            console.rule(
                f"[cyan]Becnhmark {current}/{total}[/cyan] -> {source_path}"
            )
            return review_file(source_path, model)
        
        run = run_benchmarks(
            benchmark_paths=benchmark_paths,
            review_function=review_with_model
        )
        
        console.rule("[bold green]Benchmark results[/bold green]")
        
        console.print(f"[bold]Model:[/bold] {model}")
        console.print(f"[bold]Benchmark:[/bold]{run.total}")
        console.print(f"[green]Passed:[/green] {run.passed}")
        console.print(f"[red]Failed:[/red] {run.failed}")
        console.print(f"[yellow]False positives:[/yellow] {run.false_positives}")
        console.print(f"[yellow]False negatives:[/yellow] {run.false_negatives}")
        console.print(f"[bold cyan]Accuracy:[/bold cyan] {run.accuracy:.2%}")
        
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Benchmark Failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc
if __name__ == "__main__":
    app()
