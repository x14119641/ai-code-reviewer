from pathlib import Path


def annotate_names(names: list[str], config_path: Path) -> list[tuple[str, int]]:
    config_size = config_path.stat().st_size

    return [
        (name, config_size)
        for name in names
    ]