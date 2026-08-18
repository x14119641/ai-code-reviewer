def filter_ids(values: list[int], allowed: list[int]) -> list[int]:
    result: list[int] = []

    for value in values:
        if value in allowed:
            result.append(value)

    return sorted(result)