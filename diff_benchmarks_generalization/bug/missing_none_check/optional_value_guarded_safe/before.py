def get_settings() -> dict[str, str]:
    return {"theme": "dark"}


def get_theme() -> str:
    settings = get_settings()
    return settings["theme"]