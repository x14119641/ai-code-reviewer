import subprocess


def ping_host(host: str) -> None:
    subprocess.run(
        f"ping -c 1 {host}",
        shell=True,
        check=True,
    )