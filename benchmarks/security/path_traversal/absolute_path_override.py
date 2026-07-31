from pathlib import Path


CONFIG_DIRECTORY = Path("/opt/application/config")


def load_config() -> str:
    config_name = input("Config name: ")
    config_path = CONFIG_DIRECTORY / config_name
    return config_path.read_text()