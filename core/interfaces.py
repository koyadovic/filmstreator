from typing import List

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.searches import Search


class DAOInterface:
    def save_audiovisual_record(self, record: AudiovisualRecord):
        raise NotImplementedError

    def save_download_source_results(self, results: List[DownloadSourceResult]):
        raise NotImplementedError


class SearchInterface:
    def search(self, search: Search, sort_by=None, paginate=False, page_size=20, page=1):
        raise NotImplementedError
