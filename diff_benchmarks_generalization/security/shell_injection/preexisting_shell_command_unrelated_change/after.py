import subprocess


def ping_host(host: str) -> bool:
    command = f"ping -c 1 {host}"
    result = subprocess.run(command, shell=True, check=True)
    return result.returncode == 0