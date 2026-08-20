import hashlib


def collect_values(values: list[str]) -> list[str]:
    hashes: list[str] = []

    for value in values:
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        hashes.append(digest)

    return hashes