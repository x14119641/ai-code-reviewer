def load_config(path: str) -> str:
    config_file = open(path, encoding="utf-8")
    content = config_file.read()
    return content.strip()