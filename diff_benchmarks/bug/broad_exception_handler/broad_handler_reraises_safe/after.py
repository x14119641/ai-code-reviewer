def log_payment_failure() -> None:
    print("Payment failed")


def process_transaction() -> None:
    print("Processing transaction")


def process_payment() -> None:
    try:
        process_transaction()
    except Exception:
        log_payment_failure()
        raise