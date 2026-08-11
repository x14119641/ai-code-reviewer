def find_user(cursor, username: str):
    query = "SELECT * FROM users WHERE username = '{}'".format(username) # noqa: UP032
    return cursor.execute(query)