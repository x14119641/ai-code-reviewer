def process_order(order: dict) -> dict:
    return {
        "id": order["id"],
        "status": "processed",
    }