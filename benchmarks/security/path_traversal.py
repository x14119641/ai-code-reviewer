from pathlib import Path

UPLOADS_DIRECTORY = Path("/srv/uploads")

def read_uploaded_file(filename: str) -> str:
    path = UPLOADS_DIRECTORY / filename
    return path.read_text(encoding="utf-8")