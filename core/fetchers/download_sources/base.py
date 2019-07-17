from typing import List
import abc

from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult


class AbstractDownloadSource(metaclass=abc.ABCMeta):

    # specify a unique name for each source
    source_name = None

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @abc.abstractmethod
    def get_source_results(self) -> List[DownloadSourceResult]:
        raise NotImplementedError
