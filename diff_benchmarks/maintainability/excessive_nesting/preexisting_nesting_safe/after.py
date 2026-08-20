def log_processing() -> None:
    print("Processing values")


def process(values: list[int]) -> None:
    log_processing()

    for value in values:
        if value > 0:
            if value % 2 == 0:
                if value < 100:
                    print(value)