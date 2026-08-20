class Profile:
    def __init__(self, email: str) -> None:
        self.email = email


def get_email(profile: Profile | None) -> str:
    if profile is None:
        return "unknown"

    return profile.email