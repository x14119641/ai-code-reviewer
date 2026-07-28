from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel

app = typer.Typer(
    help="Review source coding using a local languague model", no_args_is_help=True
)
console = Console()


@app.callback()
def main() -> None:
    """Review source coding using a local languague model"""


@app.command()
def review(
    path: Path = typer.Argument(
        ...,
        help="Path to the file to review.",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
) -> None:
    """Review one soruce code file"""
    console.print(
        Panel.fit(f"Ready to review: [bold]{path}[/bold]", title="Ai Code reviewer")
    )


if __name__ == "__main__":
    app()
