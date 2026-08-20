import pickle


def load_cached_value(raw_data: bytes) -> object:
    return pickle.loads(raw_data)