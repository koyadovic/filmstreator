import random
import socket
import urllib.parse
import dns.resolver


def get_domain_from_url(url):
    return urllib.parse.urlparse(url).netloc


def domain_exists(domain):
    domain_name_servers = [
        '1.1.1.1', '8.8.8.8', '9.9.9.9', '64.6.64.6'
    ]
    random.shuffle(domain_name_servers)
    any_valid = False
    for d in domain_name_servers:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [d]
        try:
            resolver.query(domain, 'A')
            any_valid = True
        except dns.resolver.NXDOMAIN:
            pass

        if any_valid:
            return True
    return any_valid


def is_tcp_port_open(ip_address, tcp_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3.0)
    result = sock.connect_ex((ip_address, int(tcp_port)))
    sock.close()
    return result == 0


def get_index_url(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme + '://' + parsed.netloc + '/'
