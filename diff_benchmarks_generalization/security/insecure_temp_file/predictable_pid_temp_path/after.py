import os
from pathlib import Path


def save_snapshot(contents: str) -> None:
    temp_path = Path("/tmp") / f"snapshot-{os.getpid()}.tmp"

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)