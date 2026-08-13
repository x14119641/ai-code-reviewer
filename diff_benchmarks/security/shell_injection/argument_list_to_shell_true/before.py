import subprocess


def ping_host(host: str) -> None:
    subprocess.run(
        ["ping", "-c", "1", host],
        check=True,
    )