from core.fetchers.services import get_all_download_sources, get_download_source_by_name
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core import services
from core.tick_worker import Ticker

from datetime import datetime, timezone, timedelta

from concurrent.futures.thread import ThreadPoolExecutor
import concurrent


@Ticker.execute_each(interval='1-minute')
async def compile_download_links_from_audiovisual_records():
    configuration = _get_ts_configuration('last_download_fetched')
    with ThreadPoolExecutor(max_workers=10) as executor:
        for source_class in get_all_download_sources():
            source_name = source_class.source_name
            ts = configuration.data.get(source_name, 0)
            from_dt = datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)

            audiovisual_records = (
                Search
                .Builder
                .new_search(AudiovisualRecord)
                .add_condition(Condition('deleted', Condition.OPERATOR_EQUALS, False))
                .add_condition(Condition('general_information_fetched', Condition.OPERATOR_EQUALS, True))
                .add_condition(Condition('created_date', Condition.OPERATOR_GREAT_THAN, from_dt))
                .search()
            )

            futures = []
            for audiovisual_record in audiovisual_records:
                future = executor.submit(_refresh_download_results_from_source, audiovisual_record, source_class)
                futures.append(future)
                if audiovisual_record.created_date > from_dt:
                    from_dt = audiovisual_record.created_date
            configuration.data[source_name] = from_dt.timestamp()

        for future in concurrent.futures.as_completed(futures):
            future.result()
        configuration.save()


@Ticker.execute_each(interval='1-minute')
async def compile_expired_download_links():
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=60)
    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('last_check', Condition.OPERATOR_LESS_THAN, n_days_ago))
        .search(sort_by='last_check')
    )
    for download_result in download_results:
        source_class = get_download_source_by_name(download_result.source_name)
        audiovisual_record = download_result.audiovisual_record
        # TODO si la película es de este año, tocará actualizar los enlaces más a menudo,
        # TODO si la película es de hace años, es tontería. Quizá revisar links, por si alguno tiene un 404
        _refresh_download_results_from_source(audiovisual_record, source_class)


def _refresh_download_results_from_source(audiovisual_record, source_class):
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

    # limit results to 3 per each source
    results = results[:3]

    for n, result in enumerate(results):
        result.audiovisual_record = audiovisual_record
    services.save_download_source_results(results)
    audiovisual_record.save()

    # remove all old download results
    for result in old_download_results:
        result.delete()


def _get_ts_configuration(key):
    configuration = Configuration.get_configuration(key=key)
    if configuration is None:
        configuration = Configuration(key=key, data={})
    return configuration
