def calculate_total(items: list[dict]) -> float:
    return sum(
        item["price"] * item["quantity"]
        for item in items
    )


def subtotal(items: list[dict]) -> float:
    return calculate_total(items)


def invoice_total(items: list[dict]) -> float:
    return calculate_total(items)