import sqlite3


def find_user_by_email(
    connection: sqlite3.Connection,
    email: str,
):
    query = "SELECT * FROM users WHERE email = '%s'" % email
    return connection.execute(query).fetchone()