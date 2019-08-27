import re
import sys
from random import shuffle

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

from core.tools.logs import log_message
from core.tools.strings import are_similar_strings


@Ticker.execute_each(interval='1-minute')
def compile_download_links_from_audiovisual_records():
    compile_download_links_from_audiovisual_records.log(f'Current switch interval: {sys.getswitchinterval()}')

    def _get_audiovisual_records(source_class):
        source_name = source_class.source_name
        audiovisual_records = (
            Search
            .Builder
            .new_search(AudiovisualRecord)
            .add_condition(Condition('deleted', Condition.EQUALS, False))
            .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
            .add_condition(Condition(f'metadata__downloads_fetch__{source_name}', Condition.EXISTS, False))
            .search(paginate=True, page_size=20, page=1, sort_by='-global_score')
        )['results']
        return audiovisual_records

    sources = get_all_download_sources()

    for_work = []
    for source_class in sources:
        for audiovisual_record in _get_audiovisual_records(source_class):
            for_work.append((source_class, audiovisual_record))

    for_work.sort(key=lambda e: e[1].global_score, reverse=True)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for source_class, audiovisual_record in for_work:
            compile_download_links_from_audiovisual_records.log(
                f'Launching search for {audiovisual_record.name} '
                f'({audiovisual_record.year}) for source {source_class.source_name}'
            )
            future = executor.submit(
                _refresh_download_results_from_source, audiovisual_record, source_class,
                compile_download_links_from_audiovisual_records.log
            )
            future.audiovisual_record = audiovisual_record
            future.source_class = source_class
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            future.result(timeout=600)
            compile_download_links_from_audiovisual_records.log(future.log_msg)
            audiovisual_record = future.audiovisual_record
            source_class = future.source_class
            source_name = source_class.source_name
            compile_download_links_from_audiovisual_records.log(
                f'Checked {audiovisual_record.name} '
                f'({audiovisual_record.year}) with {source_name}'
            )
            with Ticker.threads_lock:
                audiovisual_record.refresh()
                if 'downloads_fetch' not in audiovisual_record.metadata:
                    audiovisual_record.metadata['downloads_fetch'] = {}
                if source_name not in audiovisual_record.metadata['downloads_fetch']:
                    audiovisual_record.metadata['downloads_fetch'][source_name] = True
                    audiovisual_record.save()
                _check_has_downloads(audiovisual_record)


@Ticker.execute_each(interval='3-days')
def recheck_downloads():
    audiovisual_records = (
        Search
        .Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('metadata__recheck_downloads', Condition.EQUALS, True))
        .search()
    )
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        sources = get_all_download_sources()
        shuffle(sources)
        for source_class in sources:
            for audiovisual_record in audiovisual_records:
                future = executor.submit(
                    _refresh_download_results_from_source, audiovisual_record, source_class
                )
                future.audiovisual_record = audiovisual_record
                future.log_str = f'Launching _refresh_download_results_from_source for ' \
                                 f'{audiovisual_record.name} with source {source_class.source_name}'
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            recheck_downloads.log(future.log_str)
            future.result(timeout=600)
            audiovisual_record = future.audiovisual_record
            audiovisual_record.refresh()
            audiovisual_record.metadata['recheck_downloads'] = False
            audiovisual_record.save()


@Ticker.execute_each(interval='3-days')
def recent_films_without_good_downloads():
    good_qualities = ['BluRayRip', 'DVDRip', 'HDTV']
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)

    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('quality', Condition.IN, good_qualities))
        .add_condition(Condition('deleted', Condition.EQUALS, False))
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

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for source_class in get_all_download_sources():
            for audiovisual_record in audiovisual_records:
                future = executor.submit(
                    _refresh_download_results_from_source, audiovisual_record, source_class
                )
                future.log_msg = f'Checking {audiovisual_record.name} with {source_class.source_name}'
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            recent_films_without_good_downloads.log(future.log_msg)
            future.result(timeout=600)


@Ticker.execute_each(interval='12-hours')
def delete_404_links():
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=60)
    download_results = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('last_check', Condition.LESS_THAN, n_days_ago))
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .search()
    )

    def _check_download_result_existence(dr):
        session = PhantomBrowsingSession(referer='https://www.google.com/')
        max_checks = 10
        current_check = 0
        audiovisual_record = dr.audiovisual_record
        while current_check < max_checks:
            current_check += 1
            response = None
            while response is None:
                session.get(dr.source_base_url_plus_relative_link)
                response = session.last_response
            if response.status_code == 404:
                log_message(f'Removed link {dr.link} with status code {response.status_code}')
                with Ticker.threads_lock:
                    dr.delete()
                    dr.audiovisual_record.metadata['recheck_downloads'] = True
                    dr.audiovisual_record.save()
                _check_has_downloads(audiovisual_record)
            return

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for download_result in download_results:
            future = executor.submit(_check_download_result_existence, download_result)
            future.log_msg = f'Checking download result {download_result.name}'
            futures.append(future)
        # wait until completed
        for future in concurrent.futures.as_completed(futures):
            delete_404_links.log(future.log_msg)
            future.result(timeout=600)


@Ticker.execute_each(interval='60-minutes')
def do_the_refresh():
    last_timestamp = do_the_refresh.data.get('last_timestamp')
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    from_datetime = None
    if last_timestamp is not None:
        from_datetime = datetime.utcfromtimestamp(last_timestamp).replace(tzinfo=timezone.utc)
    search_builder = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('updated_date', Condition.LESS_OR_EQUAL_THAN, now))
    )
    if from_datetime is not None:
        search_builder.add_condition(Condition('updated_date', Condition.GREAT_THAN, from_datetime))
    records = search_builder.search()
    for record in records:
        do_the_refresh.log(f'Checking {record.name}')
        _check_has_downloads(record)
    do_the_refresh.data.set('last_timestamp', now.timestamp())


def _refresh_download_results_from_source(audiovisual_record, source_class, logger=None):
    good_qualities = ['BluRayRip', 'DVDRip', 'HDTV']  # de verdad sólo son estos???
    download_source = source_class(audiovisual_record)
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)

    # get results found by source_class for audiovisual_record
    results = download_source.get_source_results(logger=logger)

    poor_quality_links = []
    remove_bad_links = False

    if len(results) > 0:
        # this is deleted and non deleted. ALL
        current_download_results = (
            Search
            .Builder
            .new_search(DownloadSourceResult)
            .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
            .add_condition(Condition('source_name', Condition.EQUALS, source_class.source_name))
            .search()
        )

        # this are current links, deleted and not deleted
        current_links = [odr.link for odr in current_download_results]

        # current number of non deleted good links
        number_of_good_quality_links = len([
            odr for odr in current_download_results if not odr.deleted and odr.quality in good_qualities
        ])

        # if we have 3 good links with the current ones saved and the new ones found, this must be deleted
        poor_quality_links = [
            odr for odr in current_download_results if not odr.deleted and odr.quality not in good_qualities
        ]

        # limit results to 3 per each source
        n = number_of_good_quality_links
        real_results = []

        # first we check for good links
        for result in results:
            if n >= 3:
                break
            if result.quality not in good_qualities:
                continue
            if result.link in current_links:
                continue

            if not _valid_result(result):
                if logger:
                    logger(f'[{source_class.source_name}] [{audiovisual_record.name}] Not valid link: {result.name}')
                result.metadata['validation'] = {
                    'valid': False,
                    'reason': f'Detected as invalid link for \'{audiovisual_record.name}\''
                }
                result.save()
                continue

            real_results.append(result)
            n += 1

        if len(real_results) < 2 and audiovisual_record.year >= str(n_days_ago.year):
            if audiovisual_record.metadata.get('recheck_downloads_executions', 0) <= 10:
                # if the film has less than 3 good downloads and is a recent film, mark it as
                # recheck downloads again
                audiovisual_record.refresh()
                audiovisual_record.metadata['recheck_downloads'] = True
                try:
                    audiovisual_record.metadata['recheck_downloads_executions'] += 1
                except KeyError:
                    audiovisual_record.metadata['recheck_downloads_executions'] = 1
                audiovisual_record.save()

        # if we didn't found good links, we check for whatever quality
        for result in results:
            if n >= 3:
                break
            if result.quality in ['Audio', 'Unknown']:
                continue
            if result.link in current_links:
                continue
            if result in real_results:
                continue

            if not _valid_result(result):
                if logger:
                    logger(f'[{source_class.source_name}] [{audiovisual_record.name}] Not valid link: {result.name}')
                result.metadata['validation'] = {
                    'valid': False,
                    'reason': f'Detected as invalid link for \'{audiovisual_record.name}\''
                }
                result.save()
                continue

            if logger:
                logger(f'[{source_class.source_name}] [{audiovisual_record.name}] +++ ADDING link: {result.name}')
            real_results.append(result)
            n += 1

        if len(real_results) > 0:
            with Ticker.threads_lock:
                services.save_download_source_results(real_results)

        remove_bad_links = len(real_results) + number_of_good_quality_links >= 3

    if remove_bad_links:
        with Ticker.threads_lock:
            for bad_link in poor_quality_links:
                bad_link.delete()

    _check_has_downloads(audiovisual_record)


def _valid_result(result):
    # name_remover = RemoveAudiovisualRecordNameFromString(result.audiovisual_record.name)
    # text_without_name = name_remover.replace_name_from_string(result.name)
    audiovisual_name = result.audiovisual_record.name.strip()
    search = re.search(r'(.*)(19\d{2}|20\d{2})(.*)', result.name)
    if search is None:
        # similar_audiovisual_name = result.name.replace(text_without_name, '')
        return False
    else:
        similar_audiovisual_name = search.group(1).strip()
    return are_similar_strings(audiovisual_name.lower(), similar_audiovisual_name.lower())


def _check_has_downloads(audiovisual_record):
    downloads = (
        Search
        .Builder
        .new_search(DownloadSourceResult)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('audiovisual_record', Condition.EQUALS, audiovisual_record))
        .search()
    )
    has_downloads = len(downloads) > 0
    if audiovisual_record.has_downloads is not has_downloads:
        with Ticker.threads_lock:
            audiovisual_record.has_downloads = has_downloads
            audiovisual_record.save()


def _get_ts_configuration(key):
    configuration = Configuration.get_configuration(key=key)
    if configuration is None:
        configuration = Configuration(key=key, data={})
    return configuration
