def find_existing_users(
    usernames: list[str],
    existing_users: list[str],
) -> list[str]:
    found = []

    for username in usernames:
        if username in existing_users:
            found.append(username)

    return found