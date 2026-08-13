def find_user(
    username: str,
    users: dict[str, int],
) -> int:
    missing_message = "User not found"

    raise KeyError(missing_message)
    return users[username]