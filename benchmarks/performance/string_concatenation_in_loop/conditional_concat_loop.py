def build_labels(values: list[str]) -> str:
    result = ""

    for value in values:
        if value:
            result += value + ","

    return result