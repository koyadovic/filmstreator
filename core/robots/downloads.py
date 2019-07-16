from core.fetchers.services import get_all_download_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition


async def compile_download_links_from_audiovisual_records():
    for klass in get_all_download_sources():
        audiovisual_records = (
            Search.Builder
                  .new_search(AudiovisualRecord)
                  .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
                  .add_condition(Condition('downloads__source_name', Condition.OPERATOR_NOT_IN, [klass.source_name]))
                  .search()
        )
        for audiovisual_record in audiovisual_records:
            download_source = klass(audiovisual_record)
            # TODO


compile_download_links_from_audiovisual_records.interval = '1-minute'
