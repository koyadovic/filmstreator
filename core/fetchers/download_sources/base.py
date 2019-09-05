from core.model.audiovisual import DownloadSourceResult
from core.tools.browsing import PhantomBrowsingSession
from core.tools.exceptions import DownloadSourceException
from core.tools.strings import RemoveAudiovisualRecordNameFromString, VideoQualityInStringDetector, are_similar_strings, \
    are_similar_strings_with_ratio, guess_language

from requests_html import HTML

import abc
import re


class DownloadSource(metaclass=abc.ABCMeta):
    # specify a unique name for each source
    source_name = None
    # Store links as relative links because domains change frequently
    # here you can put the base_url that will be used with relative urls
    base_url = None
    language = None  # ISO 639-2 Code, three characters
    retrieve_index_first = False  # to retrieve the index page first if needed

    enabled = True

    def __init__(self, audiovisual_record_name, year='', retrieve_index_first=False, remove_first=None):
        self._name = audiovisual_record_name
        self._year = year
        self._logger = None
        self._last_response = None
        self._remove_first = remove_first
        self.retrieve_index_first = retrieve_index_first

    def log(self, text):
        if self._logger is not None:
            self._logger(text)

    def get_source_results(self, logger=None, sleep_between_requests=30):
        self._logger = logger

        response = self._get_http_response(sleep_between_requests)
        if response is None:
            raise DownloadSourceException('Response from session was None')

        if response.status_code == 404:
            return []

        html_dom = HTML(html=response.content)
        results = []
        for a in html_dom.find('a'):
            name = a.text
            if len(name) < 4:
                continue
            link = list(a.links)[0] if len(a.links) > 0 else ''
            if link == '':
                continue

            name_remover = RemoveAudiovisualRecordNameFromString(self._name)
            text_without_name = name_remover.replace_name_from_string(name)
            quality_detector = VideoQualityInStringDetector(text_without_name)

            source_name = self.source_name
            name = name.strip()
            quality = quality_detector.quality
            if not link.lower().startswith('http'):
                link = self.base_url + link

            language = guess_language(name, default=self.language, remove_first=self._remove_first)

            result = DownloadSourceResult(
                source_name=source_name,
                name=name,
                link=link,
                quality=quality,
                lang=language,
                audiovisual_record=None
            )

            valid_result, ratio = self._valid_result(result)
            if ratio < 0.8:
                # self.log(f'--- Not valid result {name} {link}. Dropping it. {ratio}')
                pass
            else:
                self.log(f'??? Possible valid result {name} {link}. Ratio: {ratio}')
                results.append(result)

        return self.post_process_results(results)

    def relative_search_string(self, search_string) -> str:
        # here you must translate the search string to a relative url the source expects
        raise NotImplementedError

    def post_process_results(self, results):
        # overwrite this method if you need to filter the initial results fetched
        return results

    def _valid_result(self, result):
        audiovisual_name = self._name.strip()
        search = re.search(r'(.*)(19\d{2}|20\d{2})(.*)', result.name)
        if search is None:
            return False, 0.0
        else:
            similar_audiovisual_name = search.group(1).strip()
        return are_similar_strings_with_ratio(audiovisual_name.lower(), similar_audiovisual_name.lower())

    def _get_search_string(self):
        # search string is {name} or {name} {year} if year is available
        search_string = f'{self._name}'
        if self._year != '':
            search_string += f' {self._year}'
        return search_string

    def _get_http_response(self, sleep_between_requests):
        search_string = self._get_search_string()
        session = PhantomBrowsingSession(referer=self.base_url + '/')
        session.get(
            self.base_url + self.relative_search_string(search_string),
            timeout=60, logger=self._logger, retrieve_index_first=self.retrieve_index_first,
            sleep_between_requests=sleep_between_requests
        )
        self._last_response = response = session.last_response
        return response

    def __str__(self):
        return f'{self.__class__.__name__} {self.source_name}'
