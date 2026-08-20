def log_export() -> None:
    print("Writing export")


def write_export(contents: str) -> None:
    log_export()

    with open(
        "/tmp/export.tmp",
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)