def process_order(order: dict) -> dict:
    if "id" not in order:
        raise ValueError("Missing order id")

    if "items" not in order:
        raise ValueError("Missing order items")

    total = 0.0

    for item in order["items"]:
        price = item["price"]
        quantity = item["quantity"]
        total += price * quantity

    if total > 100:
        discount = total * 0.10
        total -= discount

    result = {
        "id": order["id"],
        "item_count": len(order["items"]),
        "total": total,
    }

    message = f"Order {order['id']} processed"
    print(message)

    return result