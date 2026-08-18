def process_order(order: dict[str, object]) -> dict[str, object]:
    total = float(order["total"])
    tax = total * 0.21

    customer = str(order["customer"]).strip()
    if not customer:
        raise ValueError("customer is required")

    email = str(order["email"]).strip().lower()
    if "@" not in email:
        raise ValueError("invalid email")

    discount = 0.0
    if total > 100:
        discount = total * 0.05

    discounted_total = total - discount
    final_total = discounted_total + tax

    status = "standard"
    if final_total > 500:
        status = "high_value"

    summary = {
        "customer": customer,
        "email": email,
        "total": total,
        "discount": discount,
        "tax": tax,
        "final_total": final_total,
        "status": status,
    }

    return summary


def format_order_id(order_id: int) -> str:
    return f"ORD-{order_id}"