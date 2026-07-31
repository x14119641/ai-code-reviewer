def process_orders(orders: list[dict]) -> list[dict]:
    processed = []

    for order in orders:
        if "id" not in order:
            continue

        if "customer" not in order:
            continue

        if "items" not in order:
            continue

        total = 0

        for item in order["items"]:
            total += item["price"] * item["quantity"]

        if total > 1000:
            discount = total * 0.10
        else:
            discount = 0

        final_price = total - discount

        processed.append(
            {
                "id": order["id"],
                "customer": order["customer"],
                "total": total,
                "discount": discount,
                "final_price": final_price,
            }
        )

    return processed