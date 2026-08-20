from pathlib import Path


def log_annotation() -> None:
    print("Annotating names")


def annotate_names(names: list[str], config_path: Path) -> list[tuple[str, int]]:
    log_annotation()
    results: list[tuple[str, int]] = []

    for name in names:
        config_size = config_path.stat().st_size
        results.append((name, config_size))

    return results