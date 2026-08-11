def build_report(lines: list[str]) -> str:
    report = ""

    for line in lines:
        report = report + line + "\n"

    return report