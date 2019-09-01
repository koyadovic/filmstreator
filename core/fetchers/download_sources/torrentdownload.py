from core.fetchers.download_sources.base import DownloadSource
import urllib.parse


class TorrentDownloadSource(DownloadSource):
    source_name = 'TorrentDownload'
    base_url = 'https://www.torrentdownload.ch'
    language = 'eng'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        encoded_name = urllib.parse.quote_plus(search_string.lower())
        url = f'/search?q={encoded_name}'
        return url

    def post_process_results(self, results):
        # three first links are fake
        return results[3:]
