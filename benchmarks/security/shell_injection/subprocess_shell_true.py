import subprocess


def convert_image(filename: str) -> None:
    command = f"convert {filename} output.png"

    subprocess.run(
        command,
        shell=True,
        check=True,
    )