from core.fetchers.download_sources.base import AbstractDownloadSource
from core.tools.urls import percent_encoding


class ThePirateBayDownloadSource(AbstractDownloadSource):
    source_name = 'ThePirateBay'
    base_url = 'https://proxtpb.art'
    language = 'eng'
    anchors_xpath = '//div[@class="detName"]/a'

    def relative_search_string(self) -> str:
        name = f'{self.audiovisual_record.name} {self.audiovisual_record.year}'
        encoded_name = percent_encoding(name.lower())
        url = f'/search/{encoded_name}/1/'
        return url
