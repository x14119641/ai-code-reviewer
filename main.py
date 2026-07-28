from pathlib import Path
import typer
from rich.console import Console
from rich.markdown import Markdown
from reviewer.llm import generate_review
from reviewer.prompts import build_review_prompt

app = typer.Typer()
console = Console()


@app.callback()
def main() -> None:
    """Local AI-powered code reviewer."""


@app.command()
def review(
    path: Path,
    model: str = typer.Option("qwen3.5:9b", help="Ollama model used for the review"),
) -> None:
    """Review one source code file"""
    if not path.exists():
        console.print(f"[red]File not found:[/red] {path}")
        raise typer.Exit(code=1)
    if not path.is_file():
        console.print(f"[red]Not a file:[/red] {path}")
        raise typer.Exit(code=1)

    try:
        code = path.read_text(encoding="utf-8")
    except OSError as exc:
        console.print(f"[red]Could not read the file:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    prompt = build_review_prompt(code)

    try:
        result = generate_review(prompt=prompt, model=model)
    except RuntimeError as exc:
        console.print(f"[red]Review Failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    # console.print(f"[yellow]Raw result:[/yellow] {result!r}")

    console.print(Markdown(result))


if __name__ == "__main__":
    app()
