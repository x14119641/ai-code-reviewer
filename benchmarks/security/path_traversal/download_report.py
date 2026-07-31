from pathlib import Path


REPORTS_DIRECTORY = Path("/srv/reports")


def download_report(report_name: str) -> bytes:
    report_path = REPORTS_DIRECTORY / report_name
    return report_path.read_bytes()