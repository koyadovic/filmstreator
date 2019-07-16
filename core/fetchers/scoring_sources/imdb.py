from core.fetchers.general_information.imdb import IMDBGeneralInformation
from core.fetchers.scoring_sources.base import AbstractScoringSource
from core.model.audiovisual import ScoringSource
from core.tools.exceptions import GeneralInformationException, ScoringSourceException


class IMDBScoringSource(metaclass=AbstractScoringSource, IMDBGeneralInformation):
    source_name = 'IMDB'

    @property
    def score(self) -> ScoringSource:
        try:
            value = super().score
            return ScoringSource(source_name=IMDBScoringSource.source_name, value=value)
        except GeneralInformationException as e:
            raise ScoringSourceException(e)
