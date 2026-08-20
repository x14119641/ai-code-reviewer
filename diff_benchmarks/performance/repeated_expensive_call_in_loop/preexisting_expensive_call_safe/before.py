import re


def count_matches(values: list[str]) -> int:
    count = 0

    for value in values:
        pattern = re.compile(r"^[a-z]+$")

        if pattern.match(value):
            count += 1

    return count