from pathlib import Path


def save_result(contents: str) -> None:
    temp_path = Path("/tmp") / "processing-result.tmp"

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)