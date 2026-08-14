def normalize_username(username: str) -> str:
    normalized = username.strip()
    normalized = normalized.lower()

    if not normalized:
        raise ValueError("Username cannot be empty")

    return normalized


def normalize_email(email: str) -> str:
    normalized = email.strip()
    normalized = normalized.lower()

    if not normalized:
        raise ValueError("Email cannot be empty")

    return normalized