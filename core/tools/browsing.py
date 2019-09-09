import time

from core.model.configurations import Configuration
from core.tools import browsing_proxies
from core.tools.exceptions import CoreException
from core.tools.logs import log_exception, log_message
from core.tools.network import domain_exists, get_domain_from_url, is_tcp_port_open, get_index_url

import requests
import random


class PhantomBrowsingSession:
    domain_checks = {}

    def __init__(self, referer=None, headers=None):
        self._referer = referer
        self._initial_referer = self._referer
        self._session = None
        self._identity = None
        self._last_response = None
        self._headers = headers or {}
        self._logger = None
        self.refresh_identity()

    def log(self, text):
        if self._logger:
            current_proxy = self._identity.current_proxies['https']
            self._logger(f'[PhantomBrowsingSession] [{current_proxy}] {text}')

    def get(self, url, headers=None, timeout=30, logger=None, retrieve_index_first=False, sleep_between_requests=None):
        self._logger = logger
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

            response = None
            try:
                if retrieve_index_first:
                    self.log(f'Get the index page {get_index_url(url)}')
                    self._session.get(
                        get_index_url(url),
                        proxies=self._identity.current_proxies,
                        headers=headers,
                        timeout=timeout
                    )
                    self.log('Sleeping ten seconds.')
                    time.sleep(4)

                # this is the target page
                self.log(f'Get the target page {url}')
                self._last_response = response = self._session.get(
                    url,
                    proxies=self._identity.current_proxies,
                    headers=headers,
                    timeout=timeout
                )
                response.raise_for_status()

            except requests.exceptions.HTTPError as e:
                """An HTTP error occurred."""
                log_message(e, only_file=True)
                if response is not None:
                    if response.status_code == 404:
                        # TODO La url puede estar mal construída, revisar
                        # TODO https://www.1377x.to/search/b%40%20%28batman%20parody%20film%29%202016/1/
                        # TODO el server retorna 404
                        self._identity.proxy_okay()
                        return self
                    if 400 <= response.status_code <= 500 or response.status_code in [503]:
                        self.log(f'Status {response.status_code}. Refreshing identity.')
                        self.refresh_identity()
                    else:
                        time.sleep(20)
                        tryings += 1

            except requests.exceptions.ConnectionError as e:
                """A proxy error occurred."""
                """An SSL error occurred."""
                # before mark this proxy as bad, test the name resolution and connection to the webserver
                if self.is_all_okay_with_url(url):
                    # ConnectionError
                    # is the proxy
                    self._identity.some_connection_error()
                    self.refresh_identity()
                else:
                    # web page? try again
                    log_exception(e, only_file=True)
                    tryings += 1

            except requests.exceptions.Timeout as e:
                """The request timed out."""
                # TODO think to do different things if the domain and url is okay or not.
                if self.is_all_okay_with_url(url):
                    self.log(f'{e}')
                    log_message(e, only_file=True)
                    tryings += 1
                else:
                    self.log(f'{e}')
                    log_message(e, only_file=True)
                    tryings += 1

            except requests.exceptions.ChunkedEncodingError as e:
                self.log(f'{e}')
                log_message(e, only_file=True)
                tryings += 1

            except requests.exceptions.RequestException as e:
                """An general requests error occurred."""
                self.log(f'{e}')
                log_exception(e, only_file=True)
                tryings += 1

            except Exception as e:
                self.log(f'{e}')
                log_exception(e, only_file=True)
                tryings += 1

            else:
                # Everything was okay
                self._identity.proxy_okay()
                self._referer = url
                self.log(f'All OK. Length of the response: {len(response.content)}')
                return self

            if sleep_between_requests is not None:
                self.log(f'Sleeping {sleep_between_requests} seconds.')
                time.sleep(sleep_between_requests)

    def is_all_okay_with_url(self, url):
        domain = get_domain_from_url(url)
        if not domain_exists(domain):
            raise PhantomBrowsingSession.DomainError(f'Domain {domain} cannot be resolved to an IP address')
        if domain in PhantomBrowsingSession.domain_checks:
            return PhantomBrowsingSession.domain_checks[domain]
        else:
            if not any([is_tcp_port_open(domain, 443), is_tcp_port_open(domain, 80)]):
                raise PhantomBrowsingSession.RemoteServerError(f'Cannot connect to {domain} ports 80 or 443')
            text = f'ConnectionError but domain {domain} exists and has ports 443 or 80 opened. Proxy Error'
            self.log(text)
            log_message(text, only_file=True)

            PhantomBrowsingSession.domain_checks[domain] = True
            return True

    @property
    def last_response(self):
        return self._last_response

    def refresh_identity(self):
        self._referer = self._initial_referer
        self._session = requests.Session()
        self._identity = BrowsingIdentity()

    class DomainError(CoreException):
        pass

    class RemoteServerError(CoreException):
        pass


class BrowsingIdentity:
    current_proxies = {}
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
        while proxy is None or proxy == '':
            try:
                proxy = all_proxies[random.randint(0, len(all_proxies))]
            except IndexError:
                continue
            proxy = proxy.strip()
            if proxy in config.data['bad']:
                proxy = None
        self.current_proxies = {
            'http': proxy,
            'https': proxy,
            'ftp': proxy
        }

    def some_connection_error(self):
        current_proxy = self.current_proxies['http']
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
        current_proxy = self.current_proxies['http']
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
