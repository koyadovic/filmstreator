import re
from difflib import SequenceMatcher

from core.model.audiovisual import AudiovisualRecord
from core.tick_worker import Ticker
from core.tools.browsing import PhantomBrowsingSession

# from core.tools.strings import are_similar_strings
# from concurrent.futures.thread import ThreadPoolExecutor
# from datetime import datetime, timezone, timedelta

from requests_html import HTML
import urllib.parse


@Ticker.execute_each(interval='1-minute')
def compile_trailers_for_audiovisual_records_in_youtube():
    logger = compile_trailers_for_audiovisual_records_in_youtube.log

    audiovisual_record = AudiovisualRecord.search({
        'deleted': False, 'general_information_fetched': True, 'has_downloads': True,
        'metadata__searched_trailers__youtube__exists': False, 'global_score__gte': 1.0,
        'scores__votes__exists': True,
    }, paginate=True, page_size=1, page=1, sort_by='-global_score').get('results')

    if len(audiovisual_record) == 0:
        return

    audiovisual_record = audiovisual_record[0]

    logger(f'Searching: {audiovisual_record.name}')
    search_string = f'{audiovisual_record.name.lower()} {audiovisual_record.year} trailer'
    video_id = _search(audiovisual_record.name.lower(), audiovisual_record.year, search_string, logger,
                       original_audiovisual_record=audiovisual_record)

    _mark_as_searched(audiovisual_record, 'youtube')
    if video_id is None:
        return
    audiovisual_record.refresh()
    if 'trailers' not in audiovisual_record.metadata:
        audiovisual_record.metadata['trailers'] = {}

    audiovisual_record.metadata['trailers']['youtube'] = f'https://www.youtube.com/embed/{video_id}'
    audiovisual_record.save()


def _search(film_name, year, search_text, logger, original_audiovisual_record=None):
    headers = {'Accept-Language': 'en,es;q=0.9,pt;q=0.8'}
    encoded = urllib.parse.quote_plus(search_text.strip().lower())
    session = PhantomBrowsingSession(headers=headers)
    session.get(f'https://www.youtube.com/results?search_query={encoded}&sp=CAMSAhgB', logger=logger)
    response = session.last_response
    if response is None:
        logger(f'Response searching trailer for {film_name} was None')
        raise Exception(f'Response searching trailer for {film_name} was None')
    if response.status_code != 200:
        logger(f'Status code searching trailer for {film_name} was {response.status_code}')
        raise Exception(f'Status code searching trailer for {film_name} was {response.status_code}')

    logger('Parsing response from Youtube')
    html_dom = HTML(html=response.content)

    selected_name = None
    selected_link = None
    max_ratio = None
    for a in html_dom.find('a'):
        name = a.text
        if len(name) < 4:
            continue
        link = list(a.links)[0] if len(a.links) > 0 else ''
        if link == '' or not link.startswith('/watch'):
            continue

        ar = original_audiovisual_record
        people = ar.directors + ar.writers + ar.stars
        if name.lower().startswith(film_name.lower()) and year in name and 'trailer' in name.lower():
            # it's okay, more checks:
            modified_name = name.lower()

            regex = f'(trailer|official|{year}'
            for person in people:
                for word in person.name.split(' '):
                    regex += f'|{word.lower()}'
            regex += ')'
            modified_name = re.sub(re.compile(regex), '', modified_name)
            modified_name = re.sub(r'[\W]+', ' ', modified_name)
            modified_name = re.sub(r'[\d]+', '', modified_name)
            modified_name = modified_name.strip()
            current_ratio = SequenceMatcher(None, modified_name, film_name.lower()).ratio()
            if (max_ratio is None or current_ratio > max_ratio) and current_ratio > 0.7:
                selected_name = name
                selected_link = link
                max_ratio = current_ratio

    if selected_name is None:
        logger(f'No trailer was found for {original_audiovisual_record.name}')
        return None
    else:
        logger(f'Found! {film_name} https://youtube.com{selected_link}')
    return _extract_video_id(selected_link)


def _extract_video_id(href):
    try:
        for par in href.strip().split('?')[1].split('&'):
            k, v = par.split('=')
            if k == 'v':
                return v
        return None
    except IndexError:
        return None


def _mark_as_searched(audiovisual_record, source_name):
    audiovisual_record.refresh()
    if 'searched_trailers' not in audiovisual_record.metadata:
        audiovisual_record.metadata['searched_trailers'] = {}
    audiovisual_record.metadata['searched_trailers'][source_name] = True
    audiovisual_record.save()

#
# @Ticker.execute_each(interval='24-hours')
# def check_youtube_trailer_links():
#     logger = check_youtube_trailer_links.log
#     n_days_ago = datetime.utcnow().replace(tzinfo=timezone.utc) - timedelta(days=60)
#     audiovisual_records = AudiovisualRecord.search({
#         'updated_date__lt': n_days_ago,
#         'deleted': False,
#         'metadata__searched_trailers__youtube__exists': True
#     })
#
#     logger(f'{len(audiovisual_records)} audiovisual records need to be checked')
#
#     with ThreadPoolExecutor(max_workers=3) as executor:
#         futures = []
#         for audiovisual_record in audiovisual_records:
#             future = executor.submit(_check_download_result_existence, download_result, download_sources_map, logger)
#             future.log_msg = f'Checking download result {download_result.name}'
#             futures.append(future)
#         # wait until completed
#         for future in concurrent.futures.as_completed(futures):
#             logger(future.log_msg)
#             future.result(timeout=600)
#
#
# def _check_youtube_video():
#     pass
#

# <div class="reason style-scope yt-player-error-message-renderer">El vídeo no está disponible</div>
