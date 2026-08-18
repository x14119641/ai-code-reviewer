def process_order(order: dict[str, object]) -> dict[str, object]:
    total = float(order["total"])
    tax = total * 0.21

    return {
        "total": total,
        "tax": tax,
        "final_total": total + tax,
    }