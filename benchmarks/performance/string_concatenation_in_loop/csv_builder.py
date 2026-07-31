def build_csv(rows: list[str]) -> str:
    csv = ""

    for row in rows:
        csv += row + "\n"

    return csv