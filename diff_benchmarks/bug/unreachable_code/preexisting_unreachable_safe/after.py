def find_user(
    username: str,
    users: dict[str, int],
) -> int:
    missing_message = f"User not found: {username}"

    raise KeyError(missing_message)
    return users[username]