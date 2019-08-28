from core.tools.timeouts import timeout
import socket


def domain_exists(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False


def is_tcp_port_open(ip_address, tcp_port):
    try:
        with timeout(10):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((ip_address, int(tcp_port)))
            sock.close()
            return result == 0
    except TimeoutError:
        return False
