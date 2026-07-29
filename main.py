from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from reviewer.engine import review_file, review_files, find_python_files

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

    try:
        result = review_file(path=path, model=model)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Could not read the file:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(Markdown(result))


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
            console.print(Markdown(result.review))
        console.print(f"\n[green]✓ Reviewed {total} Python files.[/green]")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        console.print(f"[red]Review Failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc


if __name__ == "__main__":
    app()
