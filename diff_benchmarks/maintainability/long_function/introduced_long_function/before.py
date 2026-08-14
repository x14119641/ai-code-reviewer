def process_order(order: dict) -> dict:
    return {
        "id": order["id"],
        "total": order["total"],
    }