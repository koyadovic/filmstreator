from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.tick_worker import Ticker
from difflib import SequenceMatcher
from requests_html import HTML

import urllib.parse
import requests


#@Ticker.execute_each(interval='1-minute')
def compile_trailers_for_audiovisual_records_in_youtube():
    audiovisual_record = (
        Search.Builder.new_search(AudiovisualRecord)
        .add_condition(Condition('deleted', Condition.EQUALS, False))
        .add_condition(Condition('general_information_fetched', Condition.EQUALS, True))
        .add_condition(Condition('metadata__searched_trailers__youtube', Condition.EXISTS, False))
        .search(paginate=True, page_size=1, page=1, sort_by='-global_score')
    )['results'][0]
    search_string = f'{audiovisual_record.name.lower()} {audiovisual_record.year} official trailer'
    video_id = _search(search_string)

    _mark_as_searched(audiovisual_record, 'youtube')
    if video_id is None:
        return
    audiovisual_record.refresh()
    if 'trailers' not in audiovisual_record.metadata:
        audiovisual_record.metadata['trailers'] = {}

    audiovisual_record.metadata['trailers']['youtube'] = f'https://www.youtube.com/embed/{video_id}'
    audiovisual_record.save()


def _search(text):
    headers = {'Accept-Language': 'en,es;q=0.9,pt;q=0.8'}
    encoded = urllib.parse.quote_plus(text.strip().lower())
    response = requests.get(f'https://www.youtube.com/results?search_query={encoded}', headers=headers)
    html_dom = HTML(html=response.content)

    max_ratio = 0.0
    selected_link = None
    for a in html_dom.find('a'):
        name = a.text
        if len(name) < 4:
            continue
        link = list(a.links)[0] if len(a.links) > 0 else ''
        if link == '':
            continue

        current_ratio = SequenceMatcher(None, name.lower(), text.lower()).ratio()
        if current_ratio > max_ratio:
            max_ratio = current_ratio
            selected_link = link
    if selected_link is None:
        return None
    if max_ratio >= 0.8:
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
