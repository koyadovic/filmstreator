from core.fetchers.download_sources.base import AbstractDownloadSource
from core.tools.urls import percent_encoding


class I337xDownloadSource(AbstractDownloadSource):
    source_name = '1337x'
    base_url = 'https://www.1377x.to'
    language = 'eng'
    anchors_xpath = '/html/body/main/div/div/div/div[2]/div[1]/table/tbody/tr/td[1]/a'

    def relative_search_string(self) -> str:
        name = f'{self.audiovisual_record.name} {self.audiovisual_record.year}'
        encoded_name = percent_encoding(name.lower())
        url = f'/search/{encoded_name}/1/'
        return url

    def not_results(self, html_content):
        possibilities = [
            'no results were returned',
            'refine your search'
        ]
        return any([p in html_content.lower() for p in possibilities])
