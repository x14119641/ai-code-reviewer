def active_users(
    usernames: list[str],
    user_status: dict[str, bool],
) -> list[str]:
    active = []

    for username in usernames:
        if user_status.get(username):
            active.append(username)

    return active