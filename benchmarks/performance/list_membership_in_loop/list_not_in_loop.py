def find_new_users(
    usernames: list[str],
    existing_users: list[str],
) -> list[str]:
    new_users = []

    for username in usernames:
        if username not in existing_users:
            new_users.append(username)

    return new_users