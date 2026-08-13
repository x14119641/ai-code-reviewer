def find_user(
    username: str,
    users: dict[str, int],
) -> int:
    return users[username]