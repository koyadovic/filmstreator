from core.model.configurations import Configuration
import os
import re


ROOT_DIRECTORY = os.path.dirname(__file__) + '/data/proxy_files/'
VALID_PATTERN = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+'


if not os.path.exists(ROOT_DIRECTORY):
    os.makedirs(ROOT_DIRECTORY)


def _get_new_file_names():
    for f_name in os.listdir(ROOT_DIRECTORY):
        if f_name.endswith('__processed'):
            continue
        yield ROOT_DIRECTORY + f_name


def _get_file_lines(f_name):
    with open(f_name, 'r') as f:
        contents = f.read()

    lines = contents.split('\n')
    for line in lines:
        line = line.strip()
        if line == '':
            continue
        if not re.search(VALID_PATTERN, line):
            continue
        yield line


def _get_proxy_config():
    return Configuration.get_configuration('proxies')


def process_new_proxy_files():
    """
    Execute this function when the application is starting up so it can
    load pending proxys before the application run
    """
    for f_name in _get_new_file_names():
        proxy_config = _get_proxy_config()
        changed = False
        for line in _get_file_lines(f_name):
            if line not in proxy_config.data['proxies']:
                proxy_config.data['proxies'].append(line)
                print(f'From file {f_name} adding {line}.')
                changed = True
        if changed:
            proxy_config.save()
            os.rename(f_name, f_name + '__processed')
