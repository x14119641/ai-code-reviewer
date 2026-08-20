def process(values: list[int]) -> None:
    for value in values:
        if value > 0:
            if value % 2 == 0:
                if value < 100:
                    print(value)