import tempfile


def write_report(contents: str) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        delete=False,
    ) as temp_file:
        temp_file.write(contents)