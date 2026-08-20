class Session:
    def refresh(self) -> None:
        print("Refreshing")


def get_session() -> Session:
    return Session()


def refresh_current_session() -> None:
    session = get_session()
    session.refresh()