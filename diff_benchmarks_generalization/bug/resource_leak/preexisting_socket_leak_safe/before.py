import socket


def send_message(host: str, port: int, message: bytes) -> int:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.sendall(message)
    return len(message)