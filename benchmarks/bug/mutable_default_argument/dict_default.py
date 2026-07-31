def update_settings(
    key: str,
    value: str,
    settings: dict[str, str] = {},
) -> dict[str, str]:
    settings[key] = value
    return settings