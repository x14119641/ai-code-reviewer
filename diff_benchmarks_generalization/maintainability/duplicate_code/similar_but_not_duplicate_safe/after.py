def validate_username(username: str) -> None:
    if not username.strip():
        raise ValueError("username is required")

    if len(username) > 50:
        raise ValueError("username is too long")


def validate_password(password: str) -> None:
    if len(password) < 12:
        raise ValueError("password is too short")

    if password.isalpha():
        raise ValueError("password must contain a non-letter")