from core.fetchers.download_sources.base import AbstractDownloadSource
import urllib.parse


class TorrentDownloadSource(AbstractDownloadSource):
    source_name = 'TorrentDownload'
    base_url = 'https://www.torrentdownload.ch'
    language = 'eng'
    anchors_xpath = '//table[@class="table2"][2]//div[@class="tt-name"]/a'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self) -> str:
        name = f'{self.audiovisual_record.name} {self.audiovisual_record.year}'
        encoded_name = urllib.parse.quote_plus(name.lower())
        url = f'/search?q={encoded_name}'
        return url

    def not_results(self, html_content):
        possibilities = [
            'no results found',
        ]
        return any([p in html_content.lower() for p in possibilities])
