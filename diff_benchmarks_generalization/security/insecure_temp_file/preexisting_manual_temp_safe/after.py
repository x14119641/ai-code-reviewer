from pathlib import Path


def log_result_write() -> None:
    print("Saving processing result")


def save_result(contents: str) -> None:
    log_result_write()

    temp_path = Path("/tmp") / "processing-result.tmp"

    with temp_path.open(
        "w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(contents)