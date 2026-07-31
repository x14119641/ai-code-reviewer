from pathlib import Path


UPLOADS_DIRECTORY = Path("/srv/uploads").resolve()


def read_uploaded_file(filename: str) -> str:
    candidate = (UPLOADS_DIRECTORY / filename).resolve()

    if not candidate.is_relative_to(UPLOADS_DIRECTORY):
        raise ValueError("Invalid upload path")

    return candidate.read_text()