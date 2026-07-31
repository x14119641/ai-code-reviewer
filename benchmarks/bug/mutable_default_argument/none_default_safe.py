def add_user(
    username: str,
    users: list[str] | None = None,
) -> list[str]:
    if users is None:
        users = []

    users.append(username)
    return users