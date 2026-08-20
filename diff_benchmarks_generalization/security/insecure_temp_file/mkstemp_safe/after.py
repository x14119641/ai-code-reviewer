import os
import tempfile


def store_intermediate(contents: str) -> None:
    file_descriptor, temp_path = tempfile.mkstemp()

    try:
        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(contents)
    finally:
        os.unlink(temp_path)