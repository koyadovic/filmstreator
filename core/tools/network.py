from core.tools.timeouts import timeout
import socket
import urllib.parse


def get_domain_from_url(url):
    return urllib.parse.urlparse(url).netloc


def domain_exists(domain):
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False


def is_tcp_port_open(ip_address, tcp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    result = sock.connect_ex((ip_address, int(tcp_port)))
    sock.close()
    return result == 0


def get_index_url(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme + '://' + parsed.netloc + '/'
