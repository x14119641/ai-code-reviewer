def find_registered_users(
    usernames: list[str],
    users: list[str],
) -> list[str]:
    registered = []

    for username in usernames:
        if username in users:
            registered.append(username)

    return registered