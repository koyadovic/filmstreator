from core.fetchers.download_sources.base import DownloadSource


class LimeTorrentsSource(DownloadSource):
    source_name = 'LimeTorrents'
    base_url = 'https://www.limetorrents.info'
    language = 'eng'
    anchors_xpath = '//table[2]//div[@class="tt-name"]/a'
    retrieve_index_first = False  # to retrieve the index page first if needed

    def relative_search_string(self, search_string) -> str:
        url = f'/search/all/{self._translate_string_search(search_string)}/seeds/1/'
        return url

    def _translate_string_search(self, text):
        text = text.replace(' ', '-')
        return ''.join(
            [c if c in 'abcdefghijklmnñopqrstuvwxyzABCDEFGHIJKLMNÑOPQRSTUVWXYZ0123456789-_' else '%20' for c in text]
        )

    def post_process_results(self, results):
        # three first links are fake
        return results[3:]
