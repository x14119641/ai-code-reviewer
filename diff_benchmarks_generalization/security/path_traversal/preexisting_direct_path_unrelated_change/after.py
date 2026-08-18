from pathlib import Path


def load_report(base_dir: Path, filename: str) -> str:
    path = base_dir / filename
    content = path.read_text(encoding="utf-8")
    return content.strip()