def calculate_subtotal(items: list[dict]) -> float:
    total = 0

    for item in items:
        total += item["price"] * item["quantity"]

    return total


def count_items(items: list[dict]) -> int:
    count = 0

    for item in items:
        count += item["quantity"]

    return count