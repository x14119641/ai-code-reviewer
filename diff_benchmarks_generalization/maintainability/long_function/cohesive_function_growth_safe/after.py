def normalize_profile(profile: dict[str, str]) -> dict[str, str]:
    name = profile["name"].strip()
    email = profile["email"].strip().lower()
    city = profile["city"].strip().title()
    country = profile["country"].strip().upper()

    if not name:
        raise ValueError("name is required")

    if "@" not in email:
        raise ValueError("invalid email")

    if not city:
        raise ValueError("city is required")

    if len(country) != 2:
        raise ValueError("country must use a two-letter code")

    return {
        "name": name,
        "email": email,
        "city": city,
        "country": country,
    }