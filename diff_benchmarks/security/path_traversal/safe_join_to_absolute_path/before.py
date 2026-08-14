from pathlib import Path


def load_config(config_name: str) -> str:
    base_dir = Path("/app/config")
    safe_name = Path(config_name).name
    path = base_dir / safe_name

    return path.read_text()