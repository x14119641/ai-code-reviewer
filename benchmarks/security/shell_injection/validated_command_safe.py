import subprocess


ALLOWED_SERVICES = {
    "nginx",
    "postgresql",
    "redis",
}


def restart_service(service_name: str) -> None:
    if service_name not in ALLOWED_SERVICES:
        raise ValueError("Unsupported service")

    subprocess.run(
        ["systemctl", "restart", service_name],
        check=True,
    )