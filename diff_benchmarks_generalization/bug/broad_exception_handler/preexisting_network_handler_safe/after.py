def log_request_start() -> None:
    print("Starting request")


def send_request() -> None:
    print("Sending request")


def fetch_remote_data() -> None:
    log_request_start()

    try:
        send_request()
    except Exception:
        return