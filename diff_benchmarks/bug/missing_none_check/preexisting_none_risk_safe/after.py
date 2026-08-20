class User:
    def __init__(self, name: str) -> None:
        self.name = name


def log_lookup() -> None:
    print("Looking up user")


def find_user() -> User | None:
    return None


def get_username() -> str:
    log_lookup()
    user = find_user()
    return user.name