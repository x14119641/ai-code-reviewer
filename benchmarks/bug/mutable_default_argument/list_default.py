def add_user(
    username: str,
    users: list[str] = [],
) -> list[str]:
    users.append(username)
    return users