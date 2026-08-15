def parse_age(value: str) -> int:
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("Age is required")

    parsed = int(cleaned)

    if parsed < 0:
        raise ValueError("Age cannot be negative")

    result = parsed
    return result


def parse_score(value: str) -> int:
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("Score is required")

    parsed = int(cleaned)

    if parsed < 0:
        raise ValueError("Score cannot be negative")

    result = parsed
    return result