def find_user(
    username: str,
    users: dict[str, int],
) -> int:
    raise KeyError(username)
    return users[username]