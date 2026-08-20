import tempfile


def save_snapshot(contents: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)