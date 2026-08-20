import json


def load_preferences(raw_data: str) -> dict[str, object]:
    return json.loads(raw_data)