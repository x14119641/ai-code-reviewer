def find_registered_users(
    usernames: list[str],
    users: dict[str, int],
) -> list[str]:
    registered_users = []

    for username in usernames:
        if username in users:
            registered_users.append(username)

    return registered_users