from pathlib import Path


def load_report(base_dir: Path, filename: str) -> str:
    path = base_dir / filename
    return path.read_text(encoding="utf-8")