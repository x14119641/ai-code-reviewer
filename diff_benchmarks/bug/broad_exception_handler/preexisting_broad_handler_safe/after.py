def log_job_start() -> None:
    print("Starting job")


def run_job() -> None:
    print("Running job")


def process_job() -> None:
    log_job_start()

    try:
        run_job()
    except Exception:
        pass