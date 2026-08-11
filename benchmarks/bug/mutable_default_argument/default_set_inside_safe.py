def add_permission(
    permission: str,
    permissions: set[str] | None = None,
) -> set[str]:
    if permissions is None:
        permissions = set()

    permissions.add(permission)
    return permissions