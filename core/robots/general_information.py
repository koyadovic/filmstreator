import os
from urllib.error import HTTPError

from core.fetchers.services import get_all_general_information_sources
from core.model.audiovisual import AudiovisualRecord
from core.tick_worker import Ticker
from core.tools.exceptions import GeneralInformationException
from core.tools.logs import log_exception, log_message

from concurrent.futures.thread import ThreadPoolExecutor

import concurrent
import urllib.request


@Ticker.execute_each(interval='1-minute')
def autocomplete_general_information_for_empty_audiovisual_records():

    audiovisual_records = AudiovisualRecord.search({
        'deleted': False, 'general_information_fetched': False,
    }, paginate=True, page_size=100, page=1).get('results')

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for audiovisual_record in audiovisual_records:
            for general_information_klass in get_all_general_information_sources():
                future = executor.submit(_update, audiovisual_record, general_information_klass)
                future.log_msg = f'Check {audiovisual_record.name} with {general_information_klass.source_name}'
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            autocomplete_general_information_for_empty_audiovisual_records.log(future.log_msg)
            future.result(timeout=600)


def _update(audiovisual_record, general_information_klass):
    general_information = general_information_klass(audiovisual_record)
    try:
        audiovisual_record.summary = general_information.summary
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
        if audiovisual_record.name != general_information.name:
            exists = len(AudiovisualRecord.search({'name': general_information.name})) > 0
            if not exists:
                audiovisual_record.name = general_information.name
                audiovisual_record.slug = None
            else:
                audiovisual_record.delete()
                return
        audiovisual_record.general_information_fetched = True
        audiovisual_record.save()

    except GeneralInformationException as e:
        log_message(str(e), only_file=True)
        audiovisual_record.delete()


@Ticker.execute_each(interval='1-minute')
def autocomplete_missing_summaries():
    audiovisual_records_without_summary_key = AudiovisualRecord.search(
        {'deleted': False, 'summary__exists': False},
        paginate=True, page_size=100, page=1
    ).get('results')

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for audiovisual_record in audiovisual_records_without_summary_key:
            for general_information_klass in get_all_general_information_sources():
                future = executor.submit(_update_only_summary, audiovisual_record, general_information_klass)
                future.log_msg = f'Check summary of {audiovisual_record.name} with ' \
                                 f'{general_information_klass.source_name}'
                futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            autocomplete_missing_summaries.log(future.log_msg)
            future.result(timeout=600)


def _update_only_summary(audiovisual_record, general_information_klass):
    general_information = general_information_klass(audiovisual_record)
    try:
        summary = general_information.summary
    except GeneralInformationException:
        summary = ''

    summary = summary or ''
    audiovisual_record.summary = summary
    audiovisual_record.save()


@Ticker.execute_each(interval='1-minute')
def save_audiovisual_images_locally():
    local_root_path = save_audiovisual_images_locally.data.get('local_root_path', None)
    web_server_root_path = save_audiovisual_images_locally.data.get('web_server_root_path', None)
    if local_root_path is None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        core_directory = os.path.dirname(current_directory)
        media_directory = os.path.dirname(core_directory) + '/media/'
        local_root_path = os.path.join(media_directory, 'ai')
        save_audiovisual_images_locally.data.set('local_root_path', local_root_path)
    if web_server_root_path is None:
        web_server_root_path = '/media/ai/'
        save_audiovisual_images_locally.data.set('web_server_root_path', web_server_root_path)

    audiovisual_records = AudiovisualRecord.search(
        {
            'deleted': False, 'general_information_fetched': True,
            'has_downloads': True, 'metadata__local_image__exists': False
        },
        paginate=True, page_size=10, page=1, sort_by='-global_score'
    ).get('results')

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for audiovisual_record in audiovisual_records:
            future = executor.submit(
                _save_audiovisual_image_locally,
                audiovisual_record,
                local_root_path,
                web_server_root_path
            )
            future.log_msg = f'Saving image to local for {audiovisual_record.name} ({audiovisual_record.year})'
            futures.append(future)
        for future in concurrent.futures.as_completed(futures):
            save_audiovisual_images_locally.log(future.log_msg)
            future.result(timeout=600)


def _save_audiovisual_image_locally(audiovisual_record, local_root_path, web_server_root_path):
    audiovisual_record.refresh()
    if len(audiovisual_record.images) == 0:
        return
    remote_image = audiovisual_record.images[0]
    if not remote_image.startswith('http'):
        return
    filename = remote_image.split('/')[-1]
    try:
        os.makedirs(os.path.join(local_root_path, audiovisual_record.slug))
    except FileExistsError:
        pass
    local_target = os.path.join(os.path.join(local_root_path, audiovisual_record.slug), filename)
    web_server_target = os.path.join(os.path.join(web_server_root_path, audiovisual_record.slug), filename)
    audiovisual_record.images.append(audiovisual_record.images[0])  # as a backup
    try:
        urllib.request.urlretrieve(audiovisual_record.images[0], local_target)
        audiovisual_record.images[0] = web_server_target
        audiovisual_record.metadata['local_image'] = True
        audiovisual_record.save()
    except (HTTPError, FileNotFoundError) as e:
        log_exception(e, only_file=True)
