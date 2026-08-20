import json


def attach_settings(
    users: list[str],
    raw_settings: str,
) -> list[tuple[str, dict[str, object]]]:
    settings = json.loads(raw_settings)

    return [
        (user, settings)
        for user in users
    ]