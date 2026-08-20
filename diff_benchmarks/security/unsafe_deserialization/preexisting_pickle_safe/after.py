import pickle


def log_cache_read() -> None:
    print("Reading cached value")


def load_cached_value(raw_data: bytes) -> object:
    log_cache_read()
    return pickle.loads(raw_data)