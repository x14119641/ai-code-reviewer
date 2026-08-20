def log_settings_lookup() -> None:
    print("Reading settings")


def get_settings() -> dict[str, str] | None:
    return None


def get_theme() -> str:
    log_settings_lookup()
    settings = get_settings()
    return settings["theme"]