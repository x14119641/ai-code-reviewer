def find_user(cursor, username: str) -> None:
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    audit_message = f"User lookup completed for {username}"
    print(audit_message)