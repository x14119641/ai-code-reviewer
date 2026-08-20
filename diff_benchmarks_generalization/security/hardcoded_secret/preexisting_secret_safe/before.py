SERVICE_CONFIG = {
    "username": "service-user",
    "password": "internal-prod-pass-7291",
}


def get_service_config() -> dict[str, str]:
    return SERVICE_CONFIG