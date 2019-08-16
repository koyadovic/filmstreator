from core.fetchers.services import get_all_scoring_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.exceptions import ScoringSourceException
from concurrent.futures.thread import ThreadPoolExecutor

import concurrent


@Ticker.execute_each(interval='1-minute')
def compile_scores_from_audiovisual_records():
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for klass in get_all_scoring_sources():
            audiovisual_records = (
                Search.Builder
                      .new_search(AudiovisualRecord)
                      .add_condition(Condition('deleted', Condition.EQUALS, False))
                      .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
                      .add_condition(Condition('scores__source_name', Condition.NOT_IN, [klass.source_name]))
                      .search(paginate=True, page_size=20, page=1)
            )['results']

            for audiovisual_record in audiovisual_records:
                future = executor.submit(_refresh_score, klass, audiovisual_record)
                future.log_msg = f'Checking {audiovisual_record.name} with {klass.source_name}'
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            compile_scores_from_audiovisual_records.log(future.log_msg)
            future.result(timeout=600)


def _refresh_score(klass, audiovisual_record):
    source = klass(audiovisual_record)
    try:
        scoring_source_instance = source.score
        audiovisual_record.scores.append(scoring_source_instance)
        audiovisual_record.save()
    except ScoringSourceException:
        audiovisual_record.delete()
