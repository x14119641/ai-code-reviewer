from pathlib import Path


def load_config(config_name: str) -> str:
    base_dir = Path("/app/config")
    path = base_dir / config_name

    return path.read_text()