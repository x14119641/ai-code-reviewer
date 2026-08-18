def create_user(name: str, email: str) -> dict[str, str]:
    if not name.strip():
        raise ValueError("name is required")

    if "@" not in email:
        raise ValueError("invalid email")

    return {"name": name, "email": email}


def update_user(name: str, email: str) -> dict[str, str]:
    return {"name": name, "email": email}