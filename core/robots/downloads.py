from core.fetchers.services import get_all_download_sources
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.searches import Search, Condition
from core import services

from datetime import datetime, timezone, timedelta


async def compile_download_links_from_audiovisual_records():
    for source_class in get_all_download_sources():
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
            download_source = source_class(audiovisual_record)
            results = download_source.get_source_results()

            old_download_results = []
            if len(results) > 0:
                old_download_results = (
                    Search
                    .Builder
                    .new_search(DownloadSourceResult)
                    .add_condition(Condition('audiovisual_record', Condition.OPERATOR_EQUALS, audiovisual_record))
                    .add_condition(Condition('source_name', Condition.OPERATOR_EQUALS, source_class.source_name))
                    .search()
                )

            for n, result in enumerate(results):
                result.audiovisual_record = audiovisual_record
            services.save_download_source_results(results)
            audiovisual_record.downloads_fetched = True
            audiovisual_record.save()

            # remove all old download results
            for result in old_download_results:
                result.delete()


async def compile_expired_download_links():
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=120)
    affected_audiovisual_records = set()

    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('last_check', Condition.OPERATOR_LESS_THAN, n_days_ago))
        .search()
    )


"""
Intervals
"""

compile_download_links_from_audiovisual_records.interval = '1-minute'
compile_expired_download_links.interval = '5-minutes'
