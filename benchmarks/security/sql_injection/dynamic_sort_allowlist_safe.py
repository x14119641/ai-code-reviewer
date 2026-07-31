import sqlite3


ALLOWED_SORT_COLUMNS = {
    "username",
    "created_at",
}


def list_users(
    connection: sqlite3.Connection,
    sort_by: str,
):
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise ValueError("Unsupported sort column")

    query = f"SELECT * FROM users ORDER BY {sort_by}"
    return connection.execute(query).fetchall()