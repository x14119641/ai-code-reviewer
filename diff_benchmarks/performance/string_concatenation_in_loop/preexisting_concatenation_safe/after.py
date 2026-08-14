def build_report(values: list[str]) -> str:
    result = ""

    for value in values:
        result += value

    message = f"Report built with {len(values)} values"
    print(message)

    return result