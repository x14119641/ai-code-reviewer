def build_report(lines: list[str]) -> str:
    parts: list[str] = []

    for line in lines:
        parts.append(line.strip())

    return "\n".join(parts)