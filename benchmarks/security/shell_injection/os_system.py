import os


def ping_host(host: str) -> int:
    command = f"ping -c 1 {host}"
    return os.system(command)