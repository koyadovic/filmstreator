from core.fetchers.services import get_all_scoring_sources
from core.model.audiovisual import AudiovisualRecord
from core.tick_worker import Ticker
from core.tools.exceptions import ScoringSourceException
from concurrent.futures.thread import ThreadPoolExecutor

import concurrent


@Ticker.execute_each(interval='5-minutes')
def compile_scores_from_audiovisual_records():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for klass in get_all_scoring_sources():
            audiovisual_records = AudiovisualRecord.search({
                'deleted': False, 'general_information_fetched': True,
                'scores__source_name__nin': [klass.source_name]
            }, paginate=True, page_size=100, page=1).get('results')

            for audiovisual_record in audiovisual_records:
                future = executor.submit(_refresh_score, klass, audiovisual_record)
                future.log_msg = f'Checking {audiovisual_record.name} with {klass.source_name}'
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            compile_scores_from_audiovisual_records.log(future.log_msg)
            future.result(timeout=600)


@Ticker.execute_each(interval='30-seconds')
def compile_missing_votes():
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for klass in get_all_scoring_sources():
            audiovisual_records = AudiovisualRecord.search({
                'deleted': False, 'general_information_fetched': True,
                'scores__source_name': klass.source_name,
                'scores__votes__exists': False
            }, paginate=True, page_size=100, page=1, sort_by='-global_score').get('results')

            for audiovisual_record in audiovisual_records:
                future = executor.submit(_refresh_score, klass, audiovisual_record)
                future.log_msg = f'Checking missing votes {audiovisual_record.name} with {klass.source_name}'
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            compile_missing_votes.log(future.log_msg)
            future.result(timeout=600)


def _refresh_score(klass, audiovisual_record):
    source = klass(audiovisual_record)
    try:
        found = False
        scoring_source_instance = source.score
        for idx, score in enumerate(audiovisual_record.scores):
            source_name = score.source_name if hasattr(score, 'source_name') else score['source_name']
            if source_name == klass.source_name:
                audiovisual_record.scores[idx] = scoring_source_instance
                found = True
                break
        if not found:
            audiovisual_record.scores.append(scoring_source_instance)

        audiovisual_record.save()
    except ScoringSourceException:
        audiovisual_record.delete()
