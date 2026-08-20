import yaml


def load_settings(raw_data: str) -> dict[str, object]:
    return yaml.safe_load(raw_data)