from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from typing import List

import abc
from lxml import html

from core.tools.browsing import PhantomBrowsingSession
from core.tools.logs import log_exception
from core.tools.strings import RemoveAudiovisualRecordNameFromString, VideoQualityInStringDetector, ratio_of_containing_similar_string, are_similar_strings
import re


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
        trying = 0
        while results is None or len(results) == 0:
            try:
                trying += 1
                session.get(self.base_url + self.relative_search_string(), timeout=30)
                response = session.last_response
                if response is None:
                    session.refresh_identity()
                    continue
                base_tree = html.fromstring(response.content)
                results = base_tree.xpath(self.anchors_xpath)
                if len(results) == 0:
                    if trying > 4:
                        return []
                    session.refresh_identity()
            except Exception as e:
                log_exception(e)
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
            name = text.strip()
            quality = quality_detector.quality
            if not href.lower().startswith('http'):
                link = self.base_url + href
            else:
                link = href
            audiovisual_record = self.audiovisual_record
            result = DownloadSourceResult(
                source_name=source_name,
                name=name,
                link=link,
                quality=quality,
                lang=self.language,
                audiovisual_record=audiovisual_record
            )
            download_results.append(result)

        return download_results
