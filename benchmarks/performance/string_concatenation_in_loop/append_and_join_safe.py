def build_report(lines: list[str]) -> str:
    parts = []

    for line in lines:
        parts.append(line.strip())

    return "\n".join(parts)