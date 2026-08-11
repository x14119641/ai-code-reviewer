def filter_supported_roles(
    roles: list[str],
) -> list[str]:
    supported_roles = ("admin", "editor", "viewer")
    result = []

    for role in roles:
        if role in supported_roles:
            result.append(role)

    return result