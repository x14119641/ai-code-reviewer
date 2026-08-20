import os


def get_api_key() -> str:
    return os.environ["PAYMENT_API_KEY"]