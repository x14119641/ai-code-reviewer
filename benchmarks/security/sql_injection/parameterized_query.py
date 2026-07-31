import sqlite3


def find_user(connection: sqlite3.Connection, username: str):
    query = "SELECT * FROM users WHERE username = ?"
    return connection.execute(query, (username,)).fetchone()