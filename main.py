from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from reviewer.engine import review_file


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


if __name__ == "__main__":
    app()
