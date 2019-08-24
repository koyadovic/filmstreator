from core.model.audiovisual import AudiovisualRecord
import abc


class AbstractGeneralInformation(metaclass=abc.ABCMeta):
    source_name = None

    def __init__(self, audiovisual_record: AudiovisualRecord):
        self.audiovisual_record = audiovisual_record

    @property
    def main_image(self):
        raise NotImplementedError

    @property
    def name(self):
        raise NotImplementedError

    @property
    def year(self):
        raise NotImplementedError

    @property
    def summary(self):
        raise NotImplementedError

    @property
    def writers_directors_stars(self):
        raise NotImplementedError

    @property
    def genres(self):
        raise NotImplementedError

    @property
    def is_a_film(self):
        raise NotImplementedError
