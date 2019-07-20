from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from typing import List

import abc


class AbstractDownloadSource(metaclass=abc.ABCMeta):

    # specify a unique name for each source
    source_name = None

    # Store links as relative links because domains change frequently
    # here you can put the base_url that will be used with relative urls
    base_url = None

    language = None  # ISO 639-2 Code, three characters

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @abc.abstractmethod
    async def get_source_results(self) -> List[DownloadSourceResult]:
        raise NotImplementedError
