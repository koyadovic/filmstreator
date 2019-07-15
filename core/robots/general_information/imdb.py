from lxml import html
import requests

from core.model.audiovisual import AudiovisualRecord
from core.robots.general_information.tests import results_page, details_page
from core.tools.strings import are_similar_strings
from core.tools.urls import percent_encoding

"""
https://www.imdb.com/find?ref_=nv_sr_fn&q=<QUERY>&s=all

Cuando hay varios resultados, este es el primer elemento:
//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a
//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a




//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/strong/span
//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[1]/div[1]/div[1]/strong/span

probar mejor esto: quizá vas más a huevo
//*[@itemprop="ratingValue"]


# director
//*[@id="title-overview-widget"]/div[2]/div[1]/div[2]/h4  # siempre tiene Director:
//*[@id="title-overview-widget"]/div[2]/div[1]/div[2]/a  # el director en concreto


//*[@id="title-overview-widget"]/div[2]/div[1]/div[3]/h4  # siempre tiene Director:
//*[@id="title-overview-widget"]/div[2]/div[1]/div[3]/a


//div[@class="credit_summary_item"]/h4/text()  # puede ser director: writer: stars:

"""


def complete_general_information(record: AudiovisualRecord):
    name = percent_encoding(record.name)
    response = requests.get(f'https://www.imdb.com/find?ref_=nv_sr_fn&q={name}&s=all')
    tree = html.fromstring(response.content)
    first_result_node = tree.xpath('//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a')[0]
    href = first_result_node.get('href')


def _search_by_name(name):
    # //*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div/a[1]
    name = percent_encoding(name)
    response = requests.get(f'https://www.imdb.com/find?ref_=nv_sr_fn&q={name}&s=all')
    tree = html.fromstring(response.content)
    results = tree.xpath('//td[@class="result_text"]/a')
    first_result_node = results[0]  # first result of the search
    href = 'https://www.imdb.com' + first_result_node.get('href')
    response = requests.get(href)
    tree = html.fromstring(response.content)
    # tree = html.fromstring(details_page)
    writers, directors, stars = _get_writers_directors_stars(tree)
    score = _get_imdb_score(tree)
    year = _get_year(tree)
    genres = _get_genres(tree)

    # TODO images
    # TODO series/películas ??

    print(f'Writers: {writers}')
    print(f'Stars: {stars}')
    print(f'Directors: {directors}')
    print(f'Score: {score}')
    print(f'Year: {year}')
    print(f'Genres: {genres}')
    print('Main image: ' + _get_main_image(tree))
    print(f'Is a film?: {_is_a_film(tree)}')


def _get_main_image(tree):
    return tree.xpath('//div[@class="poster"]/a/img')[0].get('src')


def _get_imdb_score(tree):
    try:
        return tree.xpath('//*[@itemprop="ratingValue"]/text()')[0]
    except IndexError:
        return None


def _get_year(tree):
    try:
        return tree.xpath('//*[@id="titleYear"]/a/text()')[0]
    except IndexError:
        return None


def _get_writers_directors_stars(tree):
    possible_targets = ['director:', 'star:', 'writer:']
    directors = []
    stars = []
    writers = []
    target = None
    for container in tree.xpath('//div[@class="credit_summary_item"]/h4/text()|'
                                '//div[@class="credit_summary_item"]/a/text()'):
        if are_similar_strings(container, 'See full cast & crew'):
            continue
        target_changed = False
        for possible_target in possible_targets:
            if are_similar_strings(container, possible_target):
                target = possible_target
                target_changed = True
        if target_changed:
            continue

        if target == 'director:':
            directors.append(container)
        elif target == 'star:':
            stars.append(container)
        elif target == 'writer:':
            writers.append(container)
    return writers, directors, stars


def _get_genres(tree):
    genres = tree.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div'
                        '/a[contains(@href, "genres")]/text()')
    return genres


def _is_a_film(tree):
    return len(tree.xpath('//*[@id="title-episode-widget"]')) == 0


if __name__ == '__main__':
    # details_page
    _search_by_name('interestelar')




