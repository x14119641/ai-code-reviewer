import re


def log_matching() -> None:
    print("Checking values")


def count_matches(values: list[str]) -> int:
    log_matching()
    count = 0

    for value in values:
        pattern = re.compile(r"^[a-z]+$")

        if pattern.match(value):
            count += 1

    return count