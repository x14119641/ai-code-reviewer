def collect_valid(
    groups: list[list[int]],
) -> list[int]:
    results: list[int] = []

    for group in groups:
        if group:
            for value in group:
                if value > 0:
                    if value % 2 == 0:
                        results.append(value)

    return results