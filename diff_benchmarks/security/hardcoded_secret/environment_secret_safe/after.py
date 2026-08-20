import os


def build_headers() -> dict[str, str]:
    api_key = os.environ["SERVICE_API_KEY"]
    return {"Authorization": f"Bearer {api_key}"}