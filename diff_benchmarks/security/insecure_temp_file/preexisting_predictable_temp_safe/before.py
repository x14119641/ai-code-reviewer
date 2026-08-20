def write_export(contents: str) -> None:
    with open(
        "/tmp/export.tmp",
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)