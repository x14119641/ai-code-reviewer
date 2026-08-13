def find_user(cursor, username: str) -> None:
    cursor.execute(
        "SELECT * FROM users WHERE username = %s",
        (username,),
    )