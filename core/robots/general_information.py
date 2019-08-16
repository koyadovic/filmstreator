from core.fetchers.services import get_all_general_information_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.exceptions import GeneralInformationException
from core.tools.logs import log_exception

from concurrent.futures.thread import ThreadPoolExecutor

import concurrent


@Ticker.execute_each(interval='1-minute')
def autocomplete_general_information_for_empty_audiovisual_records():
    audiovisual_records = (
        Search.Builder.new_search(AudiovisualRecord)
                      .add_condition(Condition('deleted', Condition.EQUALS, False))
                      .add_condition(Condition('general_information_fetched', Condition.EQUALS, False))
                      .search(paginate=True, page_size=30, page=1)
    )['results']
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for audiovisual_record in audiovisual_records:
            for general_information_klass in get_all_general_information_sources():
                future = executor.submit(_update, audiovisual_record, general_information_klass)
                future.log_msg = f'Check {audiovisual_record.name} with {general_information_klass.source_name}'
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            autocomplete_general_information_for_empty_audiovisual_records.log(future.log_msg)
            future.result(timeout=600)


def _update(audiovisual_record, general_information_klass):
    general_information = general_information_klass(audiovisual_record)
    try:
        audiovisual_record.images = [general_information.main_image]
        if not bool(audiovisual_record.year):
            audiovisual_record.year = general_information.year
        (
            audiovisual_record.writers,
            audiovisual_record.directors,
            audiovisual_record.stars
        ) = general_information.writers_directors_stars
        audiovisual_record.genres = general_information.genres
        audiovisual_record.is_a_film = general_information.is_a_film
        if audiovisual_record.name != general_information.name:
            exists = len(
                Search.Builder.new_search(AudiovisualRecord)
                .add_condition(Condition('name', Condition.EQUALS, general_information.name))
                .search()
            ) > 0
            if not exists:
                audiovisual_record.name = general_information.name
            else:
                audiovisual_record.delete()
                return
        audiovisual_record.general_information_fetched = True
        audiovisual_record.save()

    except GeneralInformationException as e:
        log_exception(e)
        audiovisual_record.delete()
