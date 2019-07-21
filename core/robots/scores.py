from core.fetchers.services import get_all_scoring_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.exceptions import ScoringSourceException
from core.tools.logs import log_exception


@Ticker.execute_each(interval='1-minute')
async def compile_scores_from_audiovisual_records():
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
            except ScoringSourceException as e:
                log_exception(e)
                continue
            audiovisual_record.scores.append(scoring_source_instance)
            audiovisual_record.save()
