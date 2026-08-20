import os


def get_database_url() -> str:
    return os.environ["DATABASE_URL"]