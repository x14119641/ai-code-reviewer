def process_order(order: dict) -> dict:
    if "id" not in order:
        raise ValueError("Missing order id")

    if "customer" not in order:
        raise ValueError("Missing customer")

    if "items" not in order:
        raise ValueError("Missing items")

    normalized_items = []

    for item in order["items"]:
        name = item["name"].strip()
        quantity = int(item["quantity"])
        price = float(item["price"])

        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        if price < 0:
            raise ValueError("Price cannot be negative")

        normalized_items.append(
            {
                "name": name,
                "quantity": quantity,
                "price": price,
            }
        )

    subtotal = 0.0

    for item in normalized_items:
        subtotal += item["quantity"] * item["price"]

    if subtotal >= 200:
        discount = subtotal * 0.15
    elif subtotal >= 100:
        discount = subtotal * 0.10
    else:
        discount = 0.0

    total = subtotal - discount

    if total >= 150:
        shipping = 0.0
    else:
        shipping = 10.0

    final_total = total + shipping

    result = {
        "id": order["id"],
        "customer": order["customer"],
        "items": normalized_items,
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "total": final_total,
        "status": "processed",
    }

    return result