from pathlib import Path


def save_preview(contents: str, user_id: int) -> None:
    temp_path = Path("/tmp") / f"preview-{user_id}.tmp"

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)