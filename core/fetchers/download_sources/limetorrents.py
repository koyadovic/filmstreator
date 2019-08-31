from core.fetchers.download_sources.base import AbstractDownloadSource
import re


class LimeTorrentsSource(AbstractDownloadSource):
    source_name = 'LimeTorrents'
    base_url = 'https://www.limetorrents.info'
    language = 'eng'
    anchors_xpath = '//table[2]//div[@class="tt-name"]/a'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self) -> str:
        audiovisual_name = self.audiovisual_record.name.lower()
        audiovisual_year = self.audiovisual_record.year
        name = f'{audiovisual_name} {audiovisual_year}'
        url = f'/search/all/{self._translate(name)}/seeds/1/'
        return url

    def _translate(self, text):
        text = text.replace(' ', '-')
        return ''.join(
            [c if c in 'abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ0123456789-_' else '%20' for c in text]
        )
