from core.model.audiovisual import AudiovisualRecord
import abc


class AbstractDownloadSource(metaclass=abc.ABCMeta):

    # specify a unique name for each source
    source_name = None

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @abc.abstractmethod
    def get_download_sources(self):
        raise NotImplementedError
