def find_allowed_users(
    usernames: list[str],
    blocked_users: set[str],
) -> list[str]:
    allowed = []

    for username in usernames:
        if username not in blocked_users:
            allowed.append(username)

    return allowed