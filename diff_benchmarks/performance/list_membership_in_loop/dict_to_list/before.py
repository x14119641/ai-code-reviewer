def find_registered_users(
    usernames: list[str],
    users: dict[str, int],
) -> list[str]:
    registered = []

    for username in usernames:
        if username in users:
            registered.append(username)

    return registered