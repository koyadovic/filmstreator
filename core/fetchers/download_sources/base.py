from lxml import html
from urllib3.exceptions import MaxRetryError, ProxyError

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from typing import List

import abc

from core.tools.browsing import PhantomBrowsingSession
from core.tools.logs import log_message
from core.tools.strings import RemoveAudiovisualRecordNameFromString, VideoQualityInStringDetector


class AbstractDownloadSource(metaclass=abc.ABCMeta):

    # specify a unique name for each source
    source_name = None

    # Store links as relative links because domains change frequently
    # here you can put the base_url that will be used with relative urls
    base_url = None

    language = None  # ISO 639-2 Code, three characters

    anchors_xpath = None

    @abc.abstractmethod
    def relative_search_string(self) -> str:
        raise NotImplementedError

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    def get_source_results(self) -> List[DownloadSourceResult]:
        session = PhantomBrowsingSession(referer=self.base_url + '/')
        results = None
        tryings = 0
        while (results is None or len(results) == 0) and tryings < 5:
            try:
                session.get(self.base_url + self.relative_search_string(), timeout=30)
                response = session.last_response
                base_tree = html.fromstring(response.content)
                results = base_tree.xpath(self.anchors_xpath)
                tryings += 1
                if len(results) == 0:
                    print('Results are zero!, refreshing our identity')
                    session.refresh_identity()
            except (ConnectionResetError, OSError, TimeoutError, MaxRetryError, ProxyError) as e:
                print(f'Error: refreshing our identity ...')
                session.refresh_identity()

        if tryings >= 10:
            log_message(f'{tryings} failed tryings for {self.audiovisual_record.name} into {self.source_name}')

        download_results = self._translate(results)
        return download_results

    def _translate(self, results):
        download_results = []
        for result in results:
            text = result.text
            if text is None or len(text) < 4:
                continue

            href = result.get('href')
            name_remover = RemoveAudiovisualRecordNameFromString(self.audiovisual_record.name)
            text_without_name = name_remover.replace_name_from_string(text)
            quality_detector = VideoQualityInStringDetector(text_without_name)

            source_name = self.source_name
            name = text
            quality = quality_detector.quality
            link = self.base_url + href
            audiovisual_record = self.audiovisual_record

            download_results.append(DownloadSourceResult(
                source_name=source_name,
                name=name,
                link=link,
                quality=quality,
                lang=self.language,
                audiovisual_record=audiovisual_record
            ))

        return download_results
