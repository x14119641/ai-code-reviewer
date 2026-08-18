def normalize_profile(profile: dict[str, str]) -> dict[str, str]:
    name = profile["name"].strip()
    email = profile["email"].strip().lower()

    if not name:
        raise ValueError("name is required")

    if "@" not in email:
        raise ValueError("invalid email")

    return {
        "name": name,
        "email": email,
    }