def read_first_line(path: str) -> str:
    source_file = open(path, encoding="utf-8")
    first_line = source_file.readline()
    source_file.close()
    return first_line