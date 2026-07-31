def filter_products(
    products: list[str],
    blacklist: list[str],
) -> list[str]:
    allowed = []

    for product in products:
        if product not in blacklist:
            allowed.append(product)

    return allowed