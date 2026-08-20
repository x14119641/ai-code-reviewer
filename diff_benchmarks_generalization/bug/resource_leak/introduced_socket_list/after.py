import socket


def send_message(host: str, port: int, message: bytes) -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    client.sendall(message)