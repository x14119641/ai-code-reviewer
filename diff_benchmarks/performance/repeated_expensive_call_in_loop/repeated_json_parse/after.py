import json


def attach_settings(
    users: list[str],
    raw_settings: str,
) -> list[tuple[str, dict[str, object]]]:
    results: list[tuple[str, dict[str, object]]] = []

    for user in users:
        settings = json.loads(raw_settings)
        results.append((user, settings))

    return results