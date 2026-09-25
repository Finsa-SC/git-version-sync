import socket

def check_network() -> None:
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=5):
            ...

    except OSError:
        raise OSError(f"Network error: Network is unreachable. Unable to fetch remote tags.")