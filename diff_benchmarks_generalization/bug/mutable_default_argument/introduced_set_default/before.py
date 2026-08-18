def collect_tags(
    tags: set[str] | None = None,
) -> set[str]:
    if tags is None:
        tags = set()

    return tags