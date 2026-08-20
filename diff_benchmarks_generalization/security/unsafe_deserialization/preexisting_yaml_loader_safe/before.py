import yaml


def load_document(raw_data: str) -> object:
    return yaml.load(
        raw_data,
        Loader=yaml.Loader,
    )