

from pathlib import Path


from reviewer.llm import generate_review
from reviewer.prompts import build_review_prompt




def review_file(
    path: Path,
    model: str,
) -> None:
    """Read and review one source-code file"""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    try:
        code = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise 

    prompt = build_review_prompt(code)

    return generate_review(prompt=prompt, model=model)
