from core.fetchers.services import get_all_download_sources
from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from implementations.mongodb.model import MongoDownloadSourceResult
from core import services


async def compile_download_links_from_audiovisual_records():
    for download_source_class in get_all_download_sources():
        audiovisual_records = (
            Search
            .Builder
            .new_search(AudiovisualRecord)
            .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
            .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
            .add_condition(Condition('downloads_fetched', Condition.OPERATOR_EQUALS, False))
            .search()
        )
        for audiovisual_record in audiovisual_records:
            download_source = download_source_class(audiovisual_record)
            results = download_source.get_source_results()
            for n, result in enumerate(results):
                result.audiovisual_record_ref = audiovisual_record
                results[n] = MongoDownloadSourceResult.convert(result)

            services.save_download_source_results(results)
            audiovisual_record.downloads_fetched = True
            audiovisual_record.save()


compile_download_links_from_audiovisual_records.interval = '1-minute'
