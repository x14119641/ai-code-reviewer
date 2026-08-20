class User:
    def __init__(self, name: str) -> None:
        self.name = name


def find_user() -> User:
    return User("Alice")


def get_username() -> str:
    user = find_user()
    return user.name