def add_option(
    option: str,
    config: dict[str, list[str]] = {"options": []},
) -> dict[str, list[str]]:
    config["options"].append(option)
    return config