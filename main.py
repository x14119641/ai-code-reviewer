from pathlib import Path

import typer
from rich.console import Console
from rich.markdown import Markdown

from reviewer.engine import review_file, review_folder


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
def review_folder_command(path:Path, model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review all Python files in a folder."""
    try: 
        results= review_folder(path, model)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
            console.print(f"[red]Review Failed:[/red] {exc}")
            raise typer.Exit(code=1) from exc
    
    if not results:
        console.print(f"[yellow]No python files found.[/yellow]")
        return
    for result in results:
        console.print(f"\n[bold blue]{result.path}[bold blue]")
        console.print(Markdown(result.review))

if __name__ == "__main__":
    app()
