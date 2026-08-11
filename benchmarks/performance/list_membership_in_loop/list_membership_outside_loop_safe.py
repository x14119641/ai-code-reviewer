def is_admin(
    username: str,
    admin_users: list[str],
) -> bool:
    return username in admin_users