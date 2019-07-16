from core.fetchers.general_information.imdb import IMDBGeneralInformation
from core.fetchers.scoring_sources.base import AbstractScoringSource


class IMDBScoringSource(metaclass=AbstractScoringSource, IMDBGeneralInformation):
    pass
