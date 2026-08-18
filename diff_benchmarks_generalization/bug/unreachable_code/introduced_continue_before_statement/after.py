def collect_positive(values: list[int]) -> list[int]:
    result: list[int] = []

    for value in values:
        if value <= 0:
            continue
            result.append(0)

        result.append(value)

    return result