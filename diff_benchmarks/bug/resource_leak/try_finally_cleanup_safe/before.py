def load_config(path: str) -> str:
    with open(path, encoding="utf-8") as config_file:
        return config_file.read()