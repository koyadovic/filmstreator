from core.fetchers.download_sources.base import AbstractDownloadSource
from core.model.audiovisual import DownloadSourceResult
from core.tools.browsing import PhantomBrowsingSession
from core.tools.logs import log_message
from core.tools.strings import RemoveAudiovisualRecordNameFromString, VideoQualityInStringDetector
from core.tools.timeouts import timeout
from core.tools.urls import percent_encoding

from urllib3.exceptions import MaxRetryError, ProxyError
from typing import List
from lxml import html
import asyncio


class ThePirateBayDownloadSource(AbstractDownloadSource):
    source_name = 'ThePirateBay'
    base_url = 'https://proxtpb.art'
    language = 'eng'

    async def get_source_results(self) -> List[DownloadSourceResult]:
        session = PhantomBrowsingSession()

        name = f'{self.audiovisual_record.name} {self.audiovisual_record.year}'
        encoded_name = percent_encoding(name)

        results = None
        tryings = 0
        while (results is None or len(results) == 0) and tryings < 50:
            try:
                with timeout(30):
                    session.get(ThePirateBayDownloadSource.base_url)
                    await asyncio.sleep(2)
                    session.get(f'{ThePirateBayDownloadSource.base_url}/search/{encoded_name}/0/7/0')
                    response = session.last_response
                    base_tree = html.fromstring(response.content)
                    results = base_tree.xpath('//div[@class="detName"]/a')
                    tryings += 1
                    if len(results) == 0:
                        await asyncio.sleep(2)
                        print('Results are zero!, refreshing our identity')
                        session.refresh_identity()
            except (ConnectionResetError, OSError, TimeoutError, MaxRetryError, ProxyError):
                await asyncio.sleep(2)
                print('Error, refreshing our identity ...')
                session.refresh_identity()

        if tryings >= 50:
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

            source_name = ThePirateBayDownloadSource.source_name
            name = text
            quality = quality_detector.quality
            link = ThePirateBayDownloadSource.base_url + href
            audiovisual_record = self.audiovisual_record

            download_results.append(DownloadSourceResult(
                source_name=source_name,
                name=name,
                link=link,
                quality=quality,
                lang=ThePirateBayDownloadSource.language,
                audiovisual_record=audiovisual_record
            ))

        return download_results
