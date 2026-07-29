import subprocess


def ping_host(hostname: str) -> None:
    subprocess.run(
        f"ping -c 1 {hostname}",
        shell=True,
        check=True,
    )