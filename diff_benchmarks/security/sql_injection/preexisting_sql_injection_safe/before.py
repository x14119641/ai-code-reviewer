def find_user(cursor, username: str) -> None:
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)

    audit_message = "User lookup completed"
    print(audit_message)