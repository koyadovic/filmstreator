from core.fetchers.services import get_all_general_information_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.exceptions import GeneralInformationException
from core.tools.logs import log_exception


@Ticker.execute_each(interval='1-minute')
def autocomplete_general_information_for_empty_audiovisual_records():
    audiovisual_records = (
        Search.Builder.new_search(AudiovisualRecord)
                      .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
                      .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, False))
                      .search()
    )
    for audiovisual_record in audiovisual_records:
        for general_information_klass in get_all_general_information_sources():
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
                audiovisual_record.general_information_fetched = True
                audiovisual_record.save()
                break

            except GeneralInformationException as e:
                log_exception(e)
                audiovisual_record.delete()
                continue
