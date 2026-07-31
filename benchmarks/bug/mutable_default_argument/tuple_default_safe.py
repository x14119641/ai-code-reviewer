def supported_extensions(
    extensions: tuple[str, ...] = (
        ".txt",
        ".md",
        ".pdf",
    ),
) -> tuple[str, ...]:
    return extensions