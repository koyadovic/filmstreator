from core.model.audiovisual import AudiovisualRecord
import abc


class AbstractScoringSource(metaclass=abc.ABCMeta):

    source_name = None

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @property
    def score(self):
        raise NotImplementedError
