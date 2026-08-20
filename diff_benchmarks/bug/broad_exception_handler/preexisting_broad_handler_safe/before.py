def run_job() -> None:
    print("Running job")


def process_job() -> None:
    try:
        run_job()
    except Exception:
        pass