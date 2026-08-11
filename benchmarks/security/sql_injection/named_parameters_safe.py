def find_user(cursor, username: str):
    query = "SELECT * FROM users WHERE username = %(username)s"
    return cursor.execute(
        query,
        {"username": username},
    )