from core.fetchers.services import get_all_scoring_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.exceptions import ScoringSourceException


@Ticker.execute_each(interval='1-minute')
def compile_scores_from_audiovisual_records():
    for klass in get_all_scoring_sources():
        audiovisual_records = (
            Search.Builder
                  .new_search(AudiovisualRecord)
                  .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
                  .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
                  .add_condition(Condition('scores__source_name', Condition.OPERATOR_NOT_IN, [klass.source_name]))
                  .search()
        )

        for audiovisual_record in audiovisual_records:
            source = klass(audiovisual_record)
            try:
                scoring_source_instance = source.score
                audiovisual_record.scores.append(scoring_source_instance)
                audiovisual_record.save()
            except ScoringSourceException:
                audiovisual_record.delete()
