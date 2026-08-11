def normalize_customer(customer: dict) -> dict:
    name = customer["name"].strip().title()
    email = customer["email"].strip().lower()

    return {
        "name": name,
        "email": email,
    }


def normalize_supplier(supplier: dict) -> dict:
    name = supplier["name"].strip().title()
    email = supplier["email"].strip().lower()

    return {
        "name": name,
        "email": email,
    }