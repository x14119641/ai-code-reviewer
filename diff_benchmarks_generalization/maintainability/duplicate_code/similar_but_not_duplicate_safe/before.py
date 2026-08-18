def validate_username(username: str) -> None:
    if not username.strip():
        raise ValueError("username is required")


def validate_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError("password is too short")