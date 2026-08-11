def add_setting(
    key: str,
    value: str,
    settings: dict[str, str] | None = None,
) -> dict[str, str]:
    if settings is None:
        settings = {}

    settings[key] = value
    return settings