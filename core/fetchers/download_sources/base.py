from typing import List
import abc

import requests

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult


class AbstractDownloadSource(metaclass=abc.ABCMeta):

    # specify a unique name for each source
    source_name = None

    # Store links as relative links because domains change frequently
    # here you can put the base_url that will be used with relative urls
    base_url = None

    language = None  # ISO 639-2 Code, three characters

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @abc.abstractmethod
    def get_source_results(self) -> List[DownloadSourceResult]:
        raise NotImplementedError

    def get_headers(self):
        return {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36',
            'referer': 'https://www.google.com/',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en,es;q=0.9,pt;q=0.8',
            'cache-control': 'max-age=0',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                      'application/signed-exchange;v=b3',
            'dnt': '1',
            'upgrade-insecure-requests': '1'
        }

    def requests_get(self, url):
        return requests.get(url, headers=self.get_headers())


"""
import requests

proxies = {
  'http': 'http://10.10.1.10:3128',
  'https': 'http://10.10.1.10:1080',
}

requests.get('http://example.org', proxies=proxies)

"""