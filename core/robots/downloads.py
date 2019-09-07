import os
import random
import re
import time

from core.fetchers.services import get_all_download_sources, get_download_source_configuration
from core.model.audiovisual import AudiovisualRecord, DownloadSourceResult
from core.tick_worker import Ticker
from core.tools.browsing import PhantomBrowsingSession
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta
from concurrent.futures.thread import ThreadPoolExecutor
import concurrent

from core.tools.exceptions import DownloadSourceException
from core.tools.logs import log_exception
from core.tools.strings import are_similar_strings
import threading


DOWNLOAD_SOURCES_RESPONSES_ROOT_DIRECTORY = os.path.dirname(__file__) + '/data/download-sources-responses/'

try:
    os.makedirs(DOWNLOAD_SOURCES_RESPONSES_ROOT_DIRECTORY)
except FileExistsError:
    pass


def _check_zero_results(results, source_class, audiovisual_record, logger):
    configuration = get_download_source_configuration(source_class)

    if len(results) == 0:
        if audiovisual_record.id not in configuration.data['audiovisual_ids']:
            configuration.data['zero_results_searches'] += 1
            configuration.data['audiovisual_names'].append(audiovisual_record.name)
            configuration.data['audiovisual_ids'].append(audiovisual_record.id)
    else:
        configuration.data['zero_results_searches'] = 0
        configuration.data['audiovisual_names'] = []
        configuration.data['audiovisual_ids'] = []
    configuration.save()

    # if there is a lot of results with 0 length we do this additional check
    # get last good downloads for this source, get the film and try again
    # if results now are zero, disable the source.
    # because the html structure of the web maybe changed
    if configuration.data['zero_results_searches'] > 300:

        previous_good_search = DownloadSourceResult.search({
            'deleted': False, 'source_name': source_class.source_name
        }, paginate=True, page_size=1, page=1)

        if len(previous_good_search) > 0:
            previous_good_search = previous_good_search[0]
            previous_audiovisual_record = previous_good_search.audiovisual_record
            ds = source_class(previous_audiovisual_record.name, year=previous_audiovisual_record.year)

            ar = previous_audiovisual_record
            people = ar.directors + ar.writers + ar.stars
            remove_first = [person.name.lower() for person in people]
            results_check = ds.get_source_results(logger=logger, remove_first=remove_first)

            if len(results_check) == 0:
                configuration.refresh()
                configuration.data['enabled'] = False
                configuration.save()
            else:
                configuration.refresh()
                configuration.data['enabled'] = True
                configuration.data['zero_results_searches'] = 0
                configuration.data['audiovisual_names'] = []
                configuration.data['audiovisual_ids'] = []
                configuration.save()
        else:
            configuration.refresh()
            configuration.data['enabled'] = False
            configuration.save()

    if not configuration.data['enabled']:
        raise DownloadSourceException(f'Disabled {source_class.source_name} download source.')


def _worker_get_download_links(source_class, audiovisual_record, logger):
    source = source_class(audiovisual_record.name, year=audiovisual_record.year)

    try:
        logger(f'get downloads links for {audiovisual_record.name}')
        results = source.get_source_results(logger=logger, sleep_between_requests=60)
        logger(f'{len(results)} for {audiovisual_record.name}')

    except DownloadSourceException as e:
        log_exception(e)
        # TODO maybe increase an error counter?

    except PhantomBrowsingSession.DomainError as e:
        # domain cannot be resolved to IP address
        # disable the source
        configuration = get_download_source_configuration(source_class)
        configuration.data['enabled'] = False
        configuration.save()
        log_exception(e)

    except PhantomBrowsingSession.RemoteServerError as e:
        # cannot connect to ports 80 / 443
        log_exception(e)
        # TODO maybe increase an error counter?

    else:
        if len(results) == 0:
            resp = source._last_response
            if resp is not None:
                response_filename = _get_response_filename(audiovisual_record.name, source_class.source_name)
                with open(response_filename, 'wb') as f:
                    f.write(resp.content)

        # this check for a lot of zero results. If is reached a number, disable de source
        _check_zero_results(results, source_class, audiovisual_record, logger)

        for result in results:
            if result.quality == 'Audio':
                continue

            # if link exists do nothing
            relative_url = urlparse(result.link).path
            exists = DownloadSourceResult.search(
                {'source_name': source_class.source_name, 'link__icontains': relative_url})
            exists += DownloadSourceResult.search({'source_name': source_class.source_name, 'name': result.name})

            if len(exists) > 0:
                continue

            result.audiovisual_record = audiovisual_record
            result.save()
            logger(f'+++ Valid result {result.name} {result.link}.')

        audiovisual_record.refresh()
        if 'downloads_fetch' not in audiovisual_record.metadata:
            audiovisual_record.metadata['downloads_fetch'] = {}
        audiovisual_record.metadata['downloads_fetch'][source_class.source_name] = True
        audiovisual_record.save()
        logger(f'Marked {audiovisual_record.name} as reviewed for source {source_class.source_name}')


def _worker_collect_download_links_for_the_first_time(source_class, logger):
    """
    This search for download links for has_downloads or not has_downloads audiovisual_records
    """
    source_name = source_class.source_name
    logger(f'Begin to retrieve audiovisual records for {source_name}')
    audiovisual_records = AudiovisualRecord.search(
        {'deleted': False, 'general_information_fetched': True,
         f'metadata__downloads_fetch__{source_name}__exists': False,
         'scores__votes__exists': True,
         'global_score__gte': 1.0},
        paginate=True, page_size=50, page=1, sort_by='-global_score'
    ).get('results')
    logger(f'Read {len(audiovisual_records)} records')
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for audiovisual_record in audiovisual_records:
            logger(f'Sleeping for 30 seconds for {source_class.source_name}')
            time.sleep(30)
            future = executor.submit(_worker_get_download_links, source_class, audiovisual_record, logger)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            future.result()


@Ticker.execute_each(interval='1-minute')
def collect_download_links_for_the_first_time():
    logger = collect_download_links_for_the_first_time.log
    sources = list(get_all_download_sources())
    random.shuffle(sources)
    threads = []
    for source_class in sources:
        if not source_class.enabled:
            continue
        logger(f'Start worker for {source_class.source_name}')
        thread = threading.Thread(
            target=_worker_collect_download_links_for_the_first_time,
            args=[source_class, logger]
        )
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


@Ticker.execute_each(interval='24-hours')
def clean_domain_caches_of_phantom_browsing_session_class():
    PhantomBrowsingSession.domain_checks = {}


@Ticker.execute_each(interval='14-days')
def recent_films_search_again_for_download_links():
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=180)
    audiovisual_records = AudiovisualRecord.search({
        'deleted': False, 'general_information_fetched': True,
        'global_score__gte': 1.0,
        'metadata__downloads_fetch__exists': True, 'year__gte': n_days_ago.strftime('%Y')
    })
    for audiovisual_record in audiovisual_records:
        audiovisual_record.refresh()
        audiovisual_record.metadata['downloads_fetch'] = {}
        audiovisual_record.save()


@Ticker.execute_each(interval='24-hours')
def delete_404_links():
    logger = delete_404_links.log
    n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=60)
    download_results = DownloadSourceResult.search({
        'last_check__lt': n_days_ago,
        'deleted': False
    })
    logger(f'{len(download_results)} download results need to be checked')
    download_sources_map = {ds.source_name: ds for ds in get_all_download_sources() if ds.enabled}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for download_result in download_results:
            future = executor.submit(_check_download_result_existence, download_result, download_sources_map, logger)
            future.log_msg = f'Checking download result {download_result.name}'
            futures.append(future)
        # wait until completed
        for future in concurrent.futures.as_completed(futures):
            logger(future.log_msg)
            future.result(timeout=600)


def _check_download_result_existence(dr, download_sources_map, logger):
    logger(f'Checking {dr}')
    audiovisual_record = dr.audiovisual_record
    session = PhantomBrowsingSession(referer='https://www.google.com/')
    session.get(dr.source_base_url_plus_relative_link)
    response = session.last_response
    if response is not None and response.status_code == 404:
        dr.last_check = datetime.utcnow().replace(tzinfo=timezone.utc)
        dr.delete()
        if dr.source_name in download_sources_map:
            source_class = download_sources_map[dr.source_name]
            try:
                audiovisual_record.refresh()
                del audiovisual_record.metadata['downloads_fetch'][source_class.source_name]
                audiovisual_record.save()
            except KeyError:
                pass
    if response is None:
        raise DownloadSourceException(f'Cannot check {dr}. Response was None')
    else:
        dr.last_check = datetime.utcnow().replace(tzinfo=timezone.utc)
        dr.save()
        logger(f'{dr} is Okay!')


def _valid_result(result):
    audiovisual_name = result.audiovisual_record.name.strip()
    pattern = re.compile(f'(.*)({result.year})(.*)')
    search = re.search(pattern, result.name)
    if search is None:
        return False
    else:
        similar_audiovisual_name = search.group(1).strip()
    return are_similar_strings(audiovisual_name.lower(), similar_audiovisual_name.lower())


def _get_response_filename(audiovisual_record_name, source_class_name):
    n = 0
    audiovisual_record_name = audiovisual_record_name.replace('/', '-')
    response_filename = f'{DOWNLOAD_SOURCES_RESPONSES_ROOT_DIRECTORY}' \
                        f'{audiovisual_record_name} {source_class_name} {n}'
    while os.path.isfile(response_filename + '.html'):
        n += 1
        response_filename = f'{DOWNLOAD_SOURCES_RESPONSES_ROOT_DIRECTORY}' \
                            f'{audiovisual_record_name} {source_class_name} {n}'
    response_filename += '.html'
    response_filename = response_filename.replace(' ', '-')
    return response_filename
