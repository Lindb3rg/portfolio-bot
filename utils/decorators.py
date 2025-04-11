import socket

def check_internet_connection(host="anthropic.com", port=443, timeout=3):
    """Check if there is an internet connection by trying to connect to Anthropic's servers."""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False