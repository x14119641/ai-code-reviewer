def build_options(
    options: dict[str, str] = {},
) -> dict[str, str]:
    result = dict(options)
    result["source"] = "reviewer"
    return result