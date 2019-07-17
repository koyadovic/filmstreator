from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search


class DAOInterface:
    def save_audiovisual_record(self, record: AudiovisualRecord):
        raise NotImplementedError


class SearchInterface:
    def search(self, search: Search, sort_by=None, paginate=False, page_size=20, page=1):
        raise NotImplementedError
