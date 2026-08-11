def build_message(values: list[str]) -> str:
    count = 0

    for value in values:
        if value:
            count += 1

    return "Values found: " + str(count)