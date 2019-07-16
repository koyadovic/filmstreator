from core.fetchers.services import get_all_scoring_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core import services
from core.services import save_audiovisual_record
from core.tools.exceptions import ScoringSourceException
from core.tools.logs import log_exception


async def compile_scores_from_audiovisual_records():
    for klass in get_all_scoring_sources():
        search = (
            Search.Builder
                  .new_search(AudiovisualRecord)
                  .add_condition(Condition('downloads__source_name', Condition.OPERATOR_NOT_IN, [klass.source_name]))
                  .build()
        )

        audiovisual_records = services.search(search)
        for audiovisual_record in audiovisual_records:
            source = klass(audiovisual_record)
            try:
                scoring_source_instance = source.score
            except ScoringSourceException as e:
                log_exception(e)
                continue
            audiovisual_record.scores.append(scoring_source_instance)
            save_audiovisual_record(audiovisual_record)

compile_scores_from_audiovisual_records.interval = '30-minute'
