API_TOKEN = "tok_prod_82fa91b6"


def build_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {API_TOKEN}"}