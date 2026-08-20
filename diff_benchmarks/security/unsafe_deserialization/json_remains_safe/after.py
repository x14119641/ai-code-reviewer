import json


def load_preferences(raw_data: str) -> dict[str, object]:
    preferences = json.loads(raw_data)
    preferences["loaded"] = True
    return preferences