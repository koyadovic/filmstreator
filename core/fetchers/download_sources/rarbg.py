# from core.fetchers.download_sources.base import DownloadSource
# import urllib.parse
#
#
# class RarBgDownloadSource(DownloadSource):
#     source_name = 'RARBG'
#     base_url = 'https://rarbgmirror.org'
#     language = 'eng'
#     retrieve_index_first = True  # to retrieve the index page first if needed
#
#     def relative_search_string(self, search_string) -> str:
#         encoded_name = urllib.parse.quote_plus(search_string.lower())
#         url = f'/search/{encoded_name}/1/'
#         return url
