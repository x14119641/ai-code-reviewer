def get_settings() -> dict[str, str] | None:
    return None


def get_theme() -> str:
    settings = get_settings()

    if settings is None:
        return "default"

    return settings["theme"]