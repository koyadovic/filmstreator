from typing import List

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.configurations import Configuration
from core.model.searches import Search


class DAOInterface:
    def save_audiovisual_record(self, record: AudiovisualRecord):
        raise NotImplementedError

    def save_download_source_results(self, results: List[DownloadSourceResult]):
        raise NotImplementedError

    def delete_audiovisual_record(self, record: AudiovisualRecord):
        raise NotImplementedError

    def delete_download_source_result(self, result: DownloadSourceResult):
        raise NotImplementedError

    def get_configuration(self, key) -> Configuration:
        raise NotImplementedError

    def save_configuration(self, configuration: Configuration):
        raise NotImplementedError

    def delete_configuration(self, configuration: Configuration):
        raise NotImplementedError


class SearchInterface:
    def search(self, search: Search, sort_by=None, paginate=False, page_size=20, page=1):
        raise NotImplementedError
