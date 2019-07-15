from lxml import html
import requests

from core.model.audiovisual import AudiovisualRecord
from core import tools
from core.robots.general_information.tests import details_page
from core.tools.strings import are_similar_strings

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
    name = tools.urls.percent_encoding(record.name)
    response = requests.get(f'https://www.imdb.com/find?ref_=nv_sr_fn&q={name}&s=all')
    tree = html.fromstring(response.content)
    first_result_node = tree.xpath('//*[@id="main"]/div/div[2]/table/tbody/tr[1]/td[2]/a')[0]
    href = first_result_node.get('href')
    text = first_result_node.text_content()


def _get_imdb_score(whole_html):
    tree = html.fromstring(whole_html)
    try:
        return tree.xpath('//*[@itemprop="ratingValue"]/text()')[0]
    except IndexError:
        return None


if __name__ == '__main__':
    # details_page
    possible_targets = ['director:', 'star:', 'writer:']
    directors = []
    stars = []
    writers = []
    target = None
    tree = html.fromstring(details_page)
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

    print(f'Writers: {writers}')
    print(f'Stars: {stars}')
    print(f'Directors: {directors}')




