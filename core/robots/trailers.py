from core.model.audiovisual import AudiovisualRecord
from core.tick_worker import Ticker
from core.tools.browsing import PhantomBrowsingSession

from requests_html import HTML
import urllib.parse


#@Ticker.execute_each(interval='30-seconds')
def compile_trailers_for_audiovisual_records_in_youtube():
    logger = compile_trailers_for_audiovisual_records_in_youtube.log

    audiovisual_record = AudiovisualRecord.search({
        'deleted': False, 'general_information_fetched': True, 'has_downloads': True,
        'metadata__searched_trailers__youtube__exists': False
    }, paginate=True, page_size=1, page=1, sort_by='-global_score').get('results')[0]

    logger(f'Searching: {audiovisual_record.name}')
    search_string = f'{audiovisual_record.name.lower()} {audiovisual_record.year} official trailer'
    video_id = _search(audiovisual_record.name.lower(), audiovisual_record.year, search_string, logger)

    _mark_as_searched(audiovisual_record, 'youtube')
    if video_id is None:
        return
    audiovisual_record.refresh()
    if 'trailers' not in audiovisual_record.metadata:
        audiovisual_record.metadata['trailers'] = {}

    audiovisual_record.metadata['trailers']['youtube'] = f'https://www.youtube.com/embed/{video_id}'
    audiovisual_record.save()


def _search(film_name, year, search_text, logger):
    headers = {'Accept-Language': 'en,es;q=0.9,pt;q=0.8'}
    encoded = urllib.parse.quote_plus(search_text.strip().lower())
    session = PhantomBrowsingSession(headers=headers)
    session.get(f'https://www.youtube.com/results?search_query={encoded}&sp=CAMSAhgB')
    response = session.last_response
    if response is None:
        raise Exception(f'Response searching trailer for {film_name} was None')
    if response.status_code != 200:
        raise Exception(f'Status code searching trailer for {film_name} was {response.status_code}')
    html_dom = HTML(html=response.content)

    selected_name = None
    selected_link = None
    for a in html_dom.find('a'):
        name = a.text
        if len(name) < 4:
            continue
        link = list(a.links)[0] if len(a.links) > 0 else ''
        if link == '' or not link.startswith('/watch'):
            continue

        if name.lower().startswith(film_name.lower()) and (year in name or 'trailer' in name.lower()):
            selected_name = name
            selected_link = link
            logger(f'Found! {film_name} https://youtube.com{link}')
            break
    if selected_name is None:
        return None
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
