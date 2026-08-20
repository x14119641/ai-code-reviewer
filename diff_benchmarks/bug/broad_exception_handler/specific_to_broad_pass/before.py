def validate_order() -> None:
    raise ValueError("Invalid order")


def handle_invalid_order() -> None:
    print("Invalid order")


def process_order() -> None:
    try:
        validate_order()
    except ValueError:
        handle_invalid_order()