import getpass


def get_database_password() -> str:
    return getpass.getpass("Database password: ")