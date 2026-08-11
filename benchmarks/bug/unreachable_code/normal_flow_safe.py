def format_username(username: str) -> str:
    cleaned = username.strip()
    normalized = cleaned.lower()
    return normalized