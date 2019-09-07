import re

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
            try:
                votes = self.base_tree.xpath('//*[@itemprop="ratingCount"]/text()')[0]
                votes = re.sub(r'[\D]', '', votes)
                votes = int(votes)
            except (IndexError, ValueError, TypeError):
                votes = 1
            return ScoringSource(
                source_name=IMDBScoringSource.source_name,
                value=float(value),
                votes=votes
            )
        except IndexError:
            raise ScoringSourceException(f'Cannot locate the score for {self.audiovisual_record.name}')
