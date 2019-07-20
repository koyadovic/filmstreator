from core.fetchers.download_sources.base import AbstractDownloadSource
import urllib.parse


class RarBgDownloadSource(AbstractDownloadSource):
    source_name = 'RARBG'
    base_url = 'https://rarbgmirror.org'
    language = 'eng'
    anchors_xpath = '//table[@class="lista2t"]//tr[@class="lista2"]//a[1]'

    def relative_search_string(self) -> str:
        name = f'{self.audiovisual_record.name} {self.audiovisual_record.year}'
        encoded_name = urllib.parse.quote_plus(name.lower())
        url = f'/search/{encoded_name}/1/'
        return url
