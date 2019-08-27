from ssl import CertificateError
from core.model.configurations import Configuration
from core.tools import browsing_proxies
from core.tools.exceptions import CoreException

from requests.exceptions import ProxyError, ConnectionError, ReadTimeout, ConnectTimeout, ChunkedEncodingError
from urllib3.exceptions import MaxRetryError, NewConnectionError
from socket import getaddrinfo, gaierror
from urllib.parse import urlparse

import requests
import random


class PhantomBrowsingSession:
    def __init__(self, referer=None, headers=None):
        self._referer = referer
        self._initial_referer = self._referer
        self._session = None
        self._identity = None
        self._last_response = None
        self._headers = headers or {}
        self.refresh_identity()

    def get(self, url, headers=None, timeout=30):
        PhantomBrowsingSession._check_domain(url)

        initial_headers = self._headers
        headers = headers or {}
        initial_headers.update(**headers)
        headers = initial_headers

        tryings = 0
        max_tryings = 10
        while tryings < max_tryings:
            headers.update({'User-Agent': self._identity.user_agent})
            if self._referer:
                headers.update({'Referer': self._referer})

            try:
                response = self._session.get(url, proxies=self._identity.proxies, headers=headers, timeout=timeout)
                self._identity.proxy_okay()
                self._last_response = response
                self._referer = url
                return self

            except (ConnectTimeout, MaxRetryError, ProxyError, ConnectionError, ReadTimeout,
                    NewConnectionError, ChunkedEncodingError, CertificateError):
                self._identity.some_connection_error()
                self.refresh_identity()

            except Exception:
                tryings += 1

    @property
    def last_response(self):
        return self._last_response

    def refresh_identity(self):
        self._referer = self._initial_referer
        self._session = requests.Session()
        self._identity = BrowsingIdentity()

    @classmethod
    def _check_domain(cls, url):
        domain = urlparse(url).netloc  # extract the domain from the url
        try:
            getaddrinfo(domain, 80)
        except gaierror:
            raise PhantomBrowsingSession.InvalidURLProvided(f'Domain {domain} of url {url} does not exist')

    class InvalidURLProvided(CoreException):
        pass


class BrowsingIdentity:
    proxies = {}
    user_agent = None

    def __init__(self):
        self._get_config()
        self._cleanup_configuration()
        self._check_if_everything_its_okay()
        self.refresh()

    def refresh(self):
        self.refresh_proxy()
        self.refresh_user_agent()

    def refresh_user_agent(self):
        all_user_agents = user_agents.split('\n')
        user_agent = all_user_agents[random.randint(0, len(all_user_agents) - 1)]
        self.user_agent = user_agent

    def refresh_proxy(self):
        config = BrowsingIdentity._get_config()
        all_proxies = config.data.get('proxies', [])
        proxy = None
        while proxy is None:
            try:
                proxy = all_proxies[random.randint(0, len(all_proxies))]
            except IndexError:
                continue
            if proxy in config.data['bad']:
                proxy = None
        self.proxies = {
            'http': proxy,
            'https': proxy,
            'ftp': proxy
        }

    def some_connection_error(self):
        current_proxy = self.proxies['http']
        config = BrowsingIdentity._get_config()
        if current_proxy not in config.data['errors']:
            config.data['errors'][current_proxy] = 0
        config.data['errors'][current_proxy] += 1
        if (
            config.data['errors'][current_proxy] >= 3 and
            current_proxy not in config.data['bad']
        ):
            config.data['bad'].append(current_proxy)
        config.save()
        self._check_if_everything_its_okay()

    def proxy_okay(self):
        current_proxy = self.proxies['http']
        config = BrowsingIdentity._get_config()
        if current_proxy in config.data['errors']:
            config.data['errors'][current_proxy] = 0
            config.save()

    def _cleanup_configuration(self):
        config = BrowsingIdentity._get_config()
        config.data['bad'] = [b for b in config.data['bad'] if b in config.data['proxies']]
        to_delete = []
        for k, v in config.data['errors'].items():
            if k not in config.data['proxies']:
                to_delete.append(k)
        for k in to_delete:
            del config.data['errors'][k]
        config.save()

    def _check_if_everything_its_okay(self):
        config = BrowsingIdentity._get_config()
        try:
            data = config.data
            assert len(data['proxies']) > len(data['bad']), 'There is insufficient proxys to use'
        except AssertionError as e:
            raise BrowsingIdentity.BrowserIdentityException(e)

    class BrowserIdentityException(CoreException):
        pass

    @classmethod
    def _get_config(cls):
        proxies_config = Configuration.get_configuration('proxies')
        if proxies_config is None:
            proxies_config = Configuration(
                key='proxies',
                data={
                    'proxies': browsing_proxies.proxies.split('\n'),
                    'errors': {},
                    'bad': []
                }
            )
            proxies_config.save()
        return proxies_config


user_agents = """Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2226.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.4; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2225.0 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2224.3 Safari/537.36
Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36
Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36
Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.67 Safari/537.36
Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1944.0 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.3319.102 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2309.372 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.2117.157 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1866.237 Safari/537.36
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/4E423F
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.517 Safari/537.36
Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36
Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1664.3 Safari/537.36
Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.16 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1623.0 Safari/537.36
Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.17 Safari/537.36
Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36
"""
