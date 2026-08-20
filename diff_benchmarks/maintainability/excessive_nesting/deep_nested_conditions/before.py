def can_process(
    active: bool,
    verified: bool,
    has_permission: bool,
    available: bool,
) -> bool:
    if not active:
        return False

    if not verified:
        return False

    if not has_permission:
        return False

    return available