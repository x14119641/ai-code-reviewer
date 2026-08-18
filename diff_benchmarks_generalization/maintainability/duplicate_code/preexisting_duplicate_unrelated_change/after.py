def create_user(name: str) -> dict[str, str]:
    if not name.strip():
        raise ValueError("name is required")

    return {"name": name}


def update_user(name: str) -> dict[str, str]:
    if not name.strip():
        raise ValueError("name is required")

    return {"name": name}


def delete_user(user_id: int) -> int:
    return user_id