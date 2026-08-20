def load_config(path: str) -> str:
    config_file = open(path, encoding="utf-8")

    try:
        return config_file.read()
    finally:
        config_file.close()