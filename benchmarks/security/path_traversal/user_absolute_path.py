from pathlib import Path


REPORTS_DIR = Path("/srv/reports")


def get_report_path(report_path: str) -> Path:
    return REPORTS_DIR / report_path