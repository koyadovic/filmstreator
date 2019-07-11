from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search


class DAOInterface:
    def save_audiovisual_record(self, record: AudiovisualRecord):
        raise NotImplementedError


class SearchInterface:
    def __init__(self, klass):
        self.klass = klass

    def search(self, search: Search):
        raise NotImplementedError
