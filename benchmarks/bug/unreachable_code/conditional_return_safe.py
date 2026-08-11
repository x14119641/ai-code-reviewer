def normalize(value: int) -> int:
    if value < 0:
        return 0

    value += 1
    return value