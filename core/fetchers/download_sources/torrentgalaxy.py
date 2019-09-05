from core.fetchers.download_sources.base import DownloadSource
import urllib.parse


class TorrentGalaxyDownloadSource(DownloadSource):
    source_name = 'TorrentGalaxy'
    base_url = 'https://torrentgalaxy.to'
    language = 'eng'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        encoded_name = urllib.parse.quote_plus(search_string.lower())
        url = f'/torrents.php?search={encoded_name}&lang=0&nox=2'
        return url
