def add_permission(
    permission: str,
    permissions: set[str] = set(),
) -> set[str]:
    permissions.add(permission)
    return permissions