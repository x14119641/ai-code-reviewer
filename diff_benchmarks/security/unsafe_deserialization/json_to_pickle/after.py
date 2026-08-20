import pickle


def load_session(raw_data: bytes) -> object:
    return pickle.loads(raw_data)