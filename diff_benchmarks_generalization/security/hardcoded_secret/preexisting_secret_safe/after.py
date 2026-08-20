SERVICE_CONFIG = {
    "username": "service-user",
    "password": "internal-prod-pass-7291",
}


def log_config_access() -> None:
    print("Reading service configuration")


def get_service_config() -> dict[str, str]:
    log_config_access()
    return SERVICE_CONFIG