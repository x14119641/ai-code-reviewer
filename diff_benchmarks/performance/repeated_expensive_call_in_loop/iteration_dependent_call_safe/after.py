import json


def normalize_values(values: list[str]) -> list[object]:
    results: list[object] = []

    for value in values:
        parsed = json.loads(value)
        results.append(parsed)

    return results