def find_existing_users(
    usernames: list[str],
    existing_users: list[str],
) -> list[str]:
    existing = set(existing_users)

    found = []

    for username in usernames:
        if username in existing:
            found.append(username)

    return found