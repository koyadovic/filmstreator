

def percent_encoding(string):
    result = ''
    accepted = [c for c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-._~'.encode('utf-8')]
    for char in string.encode('utf-8'):
        result += chr(char) if char in accepted else '%{}'.format(hex(char)[2:]).upper()
    return result
