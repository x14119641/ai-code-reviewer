import os


def connect_database() -> str:
    database_url = os.environ["DATABASE_URL"]
    return database_url