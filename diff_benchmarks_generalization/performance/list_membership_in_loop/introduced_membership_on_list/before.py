def filter_ids(values: list[int], allowed: set[int]) -> list[int]:
    result: list[int] = []

    for value in values:
        if value in allowed:
            result.append(value)

    return result