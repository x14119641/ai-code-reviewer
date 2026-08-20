import re


def matching_values(values: list[str]) -> list[str]:
    pattern = re.compile(r"^[a-z]+$")

    return [
        value
        for value in values
        if pattern.match(value)
    ]