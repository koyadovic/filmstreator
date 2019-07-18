from typing import List

from core.fetchers.download_sources.base import AbstractDownloadSource
from core.model.audiovisual import DownloadSourceResult, AudiovisualRecord

import urllib.parse
from lxml import html
import requests

from core.tools.strings import RemoveAudiovisualRecordNameFromString, VideoQualityInStringDetector


class RarBgDownloadSource(AbstractDownloadSource):
    # specify a unique name for each source
    source_name = 'RARBG'

    # Store links as relative links because domains change frequently
    # here you can put the base_url that will be used with relative urls
    base_url = 'https://rarbgmirror.org'

    language = 'eng'

    def __init__(self, audiovisual_record: AudiovisualRecord):
        super().__init__(audiovisual_record)
        self._base_tree = None

    def get_source_results(self) -> List[DownloadSourceResult]:
        download_results = []

        results = self.base_tree.xpath('//table[@class="lista2t"]//tr[@class="lista2"]//a[1]')
        for result in results:
            text = result.text
            if text is None or len(text) < 4:
                continue
            href = result.get('href')

            name_remover = RemoveAudiovisualRecordNameFromString(self.audiovisual_record.name)
            text_without_name = name_remover.replace_name_from_string(text)
            quality_detector = VideoQualityInStringDetector(text_without_name)

            source_name = RarBgDownloadSource.source_name
            name = text
            quality = quality_detector.quality
            link = RarBgDownloadSource.base_url + href
            audiovisual_record_ref = self.audiovisual_record

            download_results.append(DownloadSourceResult(
                source_name=source_name,
                name=name,
                link=link,
                quality=quality,
                lang=RarBgDownloadSource.language,
                audiovisual_record_ref=audiovisual_record_ref
            ))

        return download_results

    @property
    def base_tree(self):
        if self._base_tree is not None:
            return self._base_tree

        name = self.audiovisual_record.name
        plus_encoded_name = urllib.parse.quote_plus(name)

        response = self.requests_get(
            f'{RarBgDownloadSource.base_url}/torrents.php?search={plus_encoded_name}&order=seeders&by=DESC'
        )
        self._base_tree = html.fromstring(response.content)
        print(response.content)
        return self._base_tree
