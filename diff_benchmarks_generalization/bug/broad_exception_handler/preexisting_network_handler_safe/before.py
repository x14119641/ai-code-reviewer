def send_request() -> None:
    print("Sending request")


def fetch_remote_data() -> None:
    try:
        send_request()
    except Exception:
        return