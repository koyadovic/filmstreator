from core.fetchers.new_additions.base import AbstractNewAdditions
from datetime import datetime
from lxml import html


class IMDBNewAdditions(AbstractNewAdditions):
    all_names_xpath = '//*[@id="main"]/div/div[3]/div/div/div[2]/div/div[1]/span/span[2]/a/text()'
    base_url = 'https://www.imdb.com'
    source_name = 'IMDB'

    def results_found(self, page):
        tree = html.fromstring(page)
        texts = tree.xpath('//*[@id="main"]/div/div/div/span/text()')
        if len(texts) == 0:
            return True
        text = texts[0].lower()
        return not ('no' in text and 'result' in text)

    def get_search_url(self, from_date: datetime, to_date: datetime):
        date_format = '%Y-%m-%d'
        from_date = from_date.strftime(date_format)
        to_date = to_date.strftime(date_format)
        return \
            f'{self.base_url}/search/title/?title_type=feature&' \
            f'release_date={from_date},{to_date}&countries=us&view=simple&count=250'
