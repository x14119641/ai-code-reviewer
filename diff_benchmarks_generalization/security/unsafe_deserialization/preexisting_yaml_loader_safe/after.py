import yaml


def log_document_load() -> None:
    print("Loading document")


def load_document(raw_data: str) -> object:
    log_document_load()

    return yaml.load(
        raw_data,
        Loader=yaml.Loader,
    )