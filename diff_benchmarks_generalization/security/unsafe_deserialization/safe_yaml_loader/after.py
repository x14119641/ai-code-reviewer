import yaml


def process_configuration(raw_data: str) -> dict[str, object]:
    return yaml.safe_load(raw_data)