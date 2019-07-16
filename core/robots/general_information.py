from sentry_sdk import capture_exception

from core.fetchers.services import get_all_general_information_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core import services
from core.services import save_audiovisual_record
from core.tools.exceptions import GeneralInformationException


async def autocomplete_general_information_for_empty_audiovisual_records():
    search = (Search.Builder.new_search(AudiovisualRecord)
                            .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, False))
                            .build())

    audiovisual_records = services.search(search)

    for audiovisual_record in audiovisual_records:
        for general_information_klass in get_all_general_information_sources():
            general_information = general_information_klass(audiovisual_record)
            try:
                audiovisual_record.images = [general_information.main_image]
                audiovisual_record.year = general_information.year
                (
                    audiovisual_record.writers,
                    audiovisual_record.directors,
                    audiovisual_record.stars
                ) = general_information.writers_directors_stars
                audiovisual_record.genres = general_information.genres
                audiovisual_record.is_a_film = general_information.is_a_film
                audiovisual_record.general_information_fetched = True
                save_audiovisual_record(audiovisual_record)
                break

            except GeneralInformationException as e:
                capture_exception(e)
                continue


autocomplete_general_information_for_empty_audiovisual_records.interval = '5-minute'
