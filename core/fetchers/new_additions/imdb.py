from lxml import html

from core.fetchers.new_additions.base import AbstractNewAdditions
from datetime import datetime
from typing import List


"""
https://www.imdb.com/search/title/?title_type=feature&release_date=2010-11-01,2010-11-02&count=250&view=simple


// no results!!!
//*[@id="main"]/div/div/div/span/text() == No results


//*[@id="main"]/div/div[3]/div/div[1]/div[2]/div/div[1]/span/span[2]/a
//*[@id="main"]/div/div[3]/div/div[7]/div[2]/div/div[1]/span/span[2]/a


// nombres!!!!
//*[@id="main"]/div/div[3]/div/div/div[2]/div/div[1]/span/span[2]/a/text()


/search/title/?title_type=feature&release_date=1990-01-01,1990-12-31&user_rating=7.5,10.0&countries=us&view=simple&count=250

"""


class IMDBNewAdditions(AbstractNewAdditions):
    all_names_xpath = '//*[@id="main"]/div/div[3]/div/div/div[2]/div/div[1]/span/span[2]/a/text()'
    base_url = 'https://www.imdb.com'

    def results_found(self, page):
        tree = html.fromstring(page)
        texts = tree.xpath('//*[@id="main"]/div/div/div/span/text()')
        if len(texts) == 0:
            return True
        text = texts[0].lower()
        return 'no' in text and 'result' in text

    def get_search_url(self, from_date: datetime, to_date: datetime):
        date_format = '%Y-%m-%d'
        from_date = from_date.strftime(date_format)
        to_date = to_date.strftime(date_format)
        return \
            f'{self.base_url}/search/title/?title_type=feature&' \
            f'release_date={from_date},{to_date}&countries=us&view=simple&count=250'
