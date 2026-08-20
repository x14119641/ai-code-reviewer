def write_report(contents: str) -> None:
    with open(
        "/tmp/report.tmp",
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)