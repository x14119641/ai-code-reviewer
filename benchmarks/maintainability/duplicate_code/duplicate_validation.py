def validate_username(username: str) -> bool:
    if len(username) < 3:
        return False

    if len(username) > 20:
        return False

    return True


def validate_nickname(nickname: str) -> bool:
    if len(nickname) < 3:
        return False

    if len(nickname) > 20:
        return False

    return True