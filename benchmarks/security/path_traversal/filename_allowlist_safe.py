from pathlib import Path


TEMPLATE_DIRECTORY = Path("/opt/application/templates")

ALLOWED_TEMPLATES = {
    "home.html",
    "about.html",
    "contact.html",
}


def load_template(template_name: str) -> str:
    if template_name not in ALLOWED_TEMPLATES:
        raise ValueError("Unknown template")

    template_path = TEMPLATE_DIRECTORY / template_name
    return template_path.read_text()