from pathlib import Path


def load_report(base_dir: Path, filename: str) -> str:
    safe_name = Path(filename).name
    path = base_dir / safe_name
    return path.read_text(encoding="utf-8")