from io import StringIO


def build_report(lines: list[str]) -> str:
    buffer = StringIO()

    for line in lines:
        buffer.write(line)
        buffer.write("\n")

    return buffer.getvalue()