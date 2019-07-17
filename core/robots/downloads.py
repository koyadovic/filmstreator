from core.fetchers.services import get_all_download_sources
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.searches import Search, Condition


async def compile_download_links_from_audiovisual_records():
    for klass in get_all_download_sources():
        audiovisual_records = (
            Search
            .Builder
            .new_search(AudiovisualRecord)
            .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
            .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
            .add_condition(Condition('downloads_fetched', Condition.OPERATOR_EQUALS, False))  # TODO hay que añadirlo al modelo
            .search()
        )
        for audiovisual_record in audiovisual_records:
            # TODO, continue from here
            download_source = klass(audiovisual_record)
            downloads = (
                Search
                .Builder
                .new_search(DownloadSourceResult)
                .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
            )


compile_download_links_from_audiovisual_records.interval = '1-minute'
