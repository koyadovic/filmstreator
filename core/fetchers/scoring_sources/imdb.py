from core.fetchers.general_information.imdb import IMDBGeneralInformation
from core.fetchers.scoring_sources.base import AbstractScoringSource
from core.model.audiovisual import ScoringSource
from core.tools.exceptions import ScoringSourceException


class IMDBScoringSource(IMDBGeneralInformation, AbstractScoringSource):
    source_name = 'IMDB'

    @property
    def score(self):
        try:
            value = self.base_tree.xpath('//*[@itemprop="ratingValue"]/text()')[0]
            return ScoringSource(source_name=IMDBScoringSource.source_name, value=value)
        except IndexError:
            raise ScoringSourceException(f'Cannot locate the score for {self.audiovisual_record.name}')
