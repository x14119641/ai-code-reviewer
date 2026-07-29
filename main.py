from pathlib import Path

import typer
from rich.console import Console

from reviewer.engine import review_file, review_files, find_python_files

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
        


if __name__ == "__main__":
    app()
