def prepare_invoices(orders: list[dict]) -> list[dict]:
    invoices = []

    for order in orders:
        if "customer" not in order:
            continue

        if "items" not in order:
            continue

        subtotal = 0

        for item in order["items"]:
            subtotal += item["price"] * item["quantity"]

        if subtotal >= 500:
            discount = subtotal * 0.05
        else:
            discount = 0

        final_total = subtotal - discount

        invoices.append(
            {
                "customer": order["customer"],
                "subtotal": subtotal,
                "discount": discount,
                "total": final_total,
            }
        )

    return invoices