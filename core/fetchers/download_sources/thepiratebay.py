from typing import List

from core.fetchers.download_sources.base import AbstractDownloadSource
from core.model.audiovisual import DownloadSourceResult


class ThePirateBayDownloadSource(AbstractDownloadSource):
    source_name = 'The pirate bay'
    base_url = 'https://loquesea.net'

    def get_source_results(self) -> List[DownloadSourceResult]:
        audiovisual_record = self.audiovisual_record
        # TODO
        return []
