def load_config(path: str) -> str:
    config_file = open(path, encoding="utf-8")
    return config_file.read()