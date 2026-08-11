def validate_length(value: str) -> bool:
    if len(value) < 3:
        return False

    if len(value) > 20:
        return False

    return True


def validate_username(username: str) -> bool:
    return validate_length(username)


def validate_nickname(nickname: str) -> bool:
    return validate_length(nickname)