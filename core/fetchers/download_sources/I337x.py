from core.fetchers.download_sources.base import DownloadSource
from core.tools.urls import percent_encoding


class I337xDownloadSource(DownloadSource):
    source_name = '1337x'
    base_url = 'https://www.1377x.to'
    language = 'eng'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        encoded_name = percent_encoding(search_string.lower())
        url = f'/search/{encoded_name}/1/'
        return url
