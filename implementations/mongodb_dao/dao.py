from core.interfaces import DAOInterface
from core.model.audiovisual import AudiovisualRecord


class DAOMongoDB(DAOInterface):
    def save_audiovisual_record(self, record: AudiovisualRecord):
        pass
