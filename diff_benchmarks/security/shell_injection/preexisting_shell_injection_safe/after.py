import subprocess


def ping_host(host: str) -> None:
    command = f"ping -c 1 {host}"

    subprocess.run(
        command,
        shell=True,
        check=True,
    )

    message = f"Ping completed for {host}"
    print(message)