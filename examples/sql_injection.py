import sqlite3


def get_user(connection: sqlite3.Connection, username: str):
    query = (
        f"SELECT id, username, email "
        f"FROM users "
        f"WHERE username = '{username}'"
    )

    return connection.execute(query).fetchone()