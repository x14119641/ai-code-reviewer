import subprocess


def search_logs(filename: str) -> None:
    command = [
        "grep",
        "error",
        filename,
    ]

    subprocess.run(
        command,
        check=True,
    )