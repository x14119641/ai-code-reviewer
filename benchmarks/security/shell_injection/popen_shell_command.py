import subprocess


def read_service_logs(service_name: str) -> str:
    command = f"journalctl -u {service_name}"

    process = subprocess.Popen(
        command,
        shell=True,
        text=True,
        stdout=subprocess.PIPE,
    )

    stdout, _ = process.communicate()
    return stdout