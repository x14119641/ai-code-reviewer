def rollback_transaction() -> None:
    print("Rolling back transaction")


def write_record() -> None:
    print("Writing record")


def save_record() -> None:
    try:
        write_record()
    except Exception:
        rollback_transaction()
        raise