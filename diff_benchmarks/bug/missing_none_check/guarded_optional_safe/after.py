class User:
    def __init__(self, name: str) -> None:
        self.name = name


def find_user() -> User | None:
    return None


def get_username() -> str:
    user = find_user()

    if user is None:
        return "unknown"

    return user.name