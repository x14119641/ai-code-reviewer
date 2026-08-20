import pickle


def store_payload(payload: bytes) -> object:
    return pickle.loads(payload)