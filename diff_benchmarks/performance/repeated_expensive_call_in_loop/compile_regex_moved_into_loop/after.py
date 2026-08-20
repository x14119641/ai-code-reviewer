import re


def matching_values(values: list[str]) -> list[str]:
    matches: list[str] = []

    for value in values:
        pattern = re.compile(r"^[a-z]+$")

        if pattern.match(value):
            matches.append(value)

    return matches