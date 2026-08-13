def find_user(cursor, username: str) -> None:
    cursor.execute(
        f"SELECT * FROM users WHERE username = '{username}'"
    )