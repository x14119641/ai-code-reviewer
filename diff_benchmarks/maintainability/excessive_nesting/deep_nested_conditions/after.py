def can_process(
    active: bool,
    verified: bool,
    has_permission: bool,
    available: bool,
) -> bool:
    if active:
        if verified:
            if has_permission:
                if available:
                    return True

    return False