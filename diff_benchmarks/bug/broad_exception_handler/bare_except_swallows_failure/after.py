def parse_configuration() -> None:
    raise ValueError("Invalid configuration")


def use_default_configuration() -> None:
    print("Using default configuration")


def load_configuration() -> None:
    try:
        parse_configuration()
    except:
        return