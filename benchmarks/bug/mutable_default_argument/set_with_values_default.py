def add_tag(
    tag: str,
    tags: set[str] = {"active"},
) -> set[str]:
    tags.add(tag)
    return tags