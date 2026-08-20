import tempfile


def save_preview(contents: str, user_id: int) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)