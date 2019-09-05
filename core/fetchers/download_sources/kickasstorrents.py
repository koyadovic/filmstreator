from core.fetchers.download_sources.base import DownloadSource
from core.tools.urls import percent_encoding


class KickassTorrentsDownloadSource(DownloadSource):
    source_name = 'KickassTorrents'
    base_url = 'https://katcr.co'
    language = 'eng'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        encoded_name = percent_encoding(search_string.lower())
        url = f'/katsearch/page/1/{encoded_name}'
        return url
