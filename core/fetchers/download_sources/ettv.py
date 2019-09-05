from core.fetchers.download_sources.base import DownloadSource
import urllib.parse


class ETTVDownloadSource(DownloadSource):
    source_name = 'ETTV'
    base_url = 'https://www.ettv.to'
    language = 'eng'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        encoded_name = urllib.parse.quote_plus(search_string.lower())
        url = f'/torrents-search.php?search={encoded_name}'
        return url
