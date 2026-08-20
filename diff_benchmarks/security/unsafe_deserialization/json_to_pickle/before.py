import json


def load_session(raw_data: bytes) -> dict[str, object]:
    return json.loads(raw_data.decode("utf-8")) 