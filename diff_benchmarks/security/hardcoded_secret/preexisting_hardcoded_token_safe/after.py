API_TOKEN = "tok_prod_82fa91b6"


def log_request() -> None:
    print("Building request headers")


def build_headers() -> dict[str, str]:
    log_request()
    return {"Authorization": f"Bearer {API_TOKEN}"}