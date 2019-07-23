from core.fetchers.services import get_all_download_sources
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.model.configurations import Configuration
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from core.tools.browsing import PhantomBrowsingSession
from core import services

from datetime import datetime, timezone, timedelta
from concurrent.futures.thread import ThreadPoolExecutor
import concurrent


@Ticker.execute_each(interval='1-minute')
def compile_download_links_from_audiovisual_records():
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for source_class in get_all_download_sources():
            source_name = source_class.source_name
            configuration = _get_ts_configuration(f'last_download_fetched_{source_name}')
            ts = configuration.data.get('ts', 0)
            from_dt = datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)

            audiovisual_records = (
                Search
                .Builder
                .new_search(AudiovisualRecord)
                .add_condition(Condition('deleted', Condition.EQUALS, False))
                .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
                .add_condition(Condition('created_date', Condition.GREAT_THAN, from_dt))
                .search()
            )

            for audiovisual_record in audiovisual_records:
                future = executor.submit(
                    _refresh_download_results_from_source, audiovisual_record, source_class
                )
                futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()


@Ticker.execute_each(interval='1-minute')
def recent_films_without_good_downloads():
    good_qualities = ['BluRayRip', 'DVDRip', 'HDTV']
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)

    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('quality', Condition.IN, good_qualities))
        .search()
    )
    audiovisual_records_to_exclude = [dr.audiovisual_record for dr in download_results]

    audiovisual_records = (
        Search
        .Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .add_condition(Condition('year', Condition.GREAT_OR_EQUAL_THAN, n_days_ago.strftime('%Y')))
        .search()
    )
    audiovisual_records = [ar for ar in audiovisual_records if ar not in audiovisual_records_to_exclude]

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for source_class in get_all_download_sources():
            for audiovisual_record in audiovisual_records:
                future = executor.submit(
                    _refresh_download_results_from_source, audiovisual_record, source_class
                )
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            future.result()


@Ticker.execute_each(interval='1-minute')
def delete_404_links():
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=60)
    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('last_check', Condition.LESS_THAN, n_days_ago))
        .search(sort_by='last_check')
    )

    def _check_download_result_existence(dr):
        session = PhantomBrowsingSession(referer='https://www.google.com/')
        max_checks = 10
        current_check = 0
        audiovisual_record = dr.audiovisual_record
        while current_check < max_checks:
            current_check += 1
            session.get(dr.link)
            response = session.last_response
            if response.status_code > 299:
                dr.delete()
                _check_has_downloads(audiovisual_record)
            return

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = []
        for download_result in download_results:
            future = executor.submit(_check_download_result_existence, download_result)
            futures.append(future)
        # wait until completed
        for future in concurrent.futures.as_completed(futures):
            future.result()


def _refresh_download_results_from_source(audiovisual_record, source_class):
    audiovisual_record_ts = audiovisual_record.created_date.timestamp()
    download_source = source_class(audiovisual_record)
    results = download_source.get_source_results()
    old_download_results = []
    if len(results) > 0:
        old_download_results = (
            Search
            .Builder
            .new_search(DownloadSourceResult)
            .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
            .add_condition(Condition('source_name', Condition.EQUALS, source_class.source_name))
            .search()
        )
        # limit results to 3 per each source
        results = results[:3]
        for result in results:
            result.audiovisual_record = audiovisual_record
        services.save_download_source_results(results)

    # remove all old download results
    for result in old_download_results:
        result.delete()

    configuration = _get_ts_configuration(f'last_download_fetched_{source_class.source_name}')
    ts = configuration.data.get('ts', 0)
    if audiovisual_record_ts > ts:
        configuration.data['ts'] = audiovisual_record_ts
        configuration.save()

    _check_has_downloads(audiovisual_record)


def _check_has_downloads(audiovisual_record):
    downloads = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .search()
    )
    has_downloads = len(downloads) > 0
    if audiovisual_record.has_downloads is not has_downloads:
        audiovisual_record.has_downloads = has_downloads
        audiovisual_record.save()


def _get_ts_configuration(key):
    configuration = Configuration.get_configuration(key=key)
    if configuration is None:
        configuration = Configuration(key=key, data={})
    return configuration
