import sqlite3


def find_order(
    connection: sqlite3.Connection,
    order_id: str,
):
    query = "SELECT * FROM orders WHERE id = " + order_id
    return connection.execute(query).fetchone()