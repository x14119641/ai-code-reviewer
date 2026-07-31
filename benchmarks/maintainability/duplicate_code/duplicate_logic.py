def calculate_subtotal(items: list[dict]) -> float:
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    return total


def calculate_invoice_total(items: list[dict]) -> float:
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    return total