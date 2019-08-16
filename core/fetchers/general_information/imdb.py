import re

from core.fetchers.general_information.base import AbstractGeneralInformation
from core.model.audiovisual import AudiovisualRecord, Genre, Person
from core.tools.browsing import PhantomBrowsingSession
from core.tools.exceptions import GeneralInformationException
from core.tools.strings import are_similar_strings
from core.tools.urls import percent_encoding
from lxml import html


class IMDBGeneralInformation(AbstractGeneralInformation):
    base_url = 'https://www.imdb.com'
    source_name = 'IMDB'

    def __init__(self, audiovisual_record: AudiovisualRecord):
        super().__init__(audiovisual_record)
        self._base_tree = None

    @property
    def main_image(self):
        try:
            src = self.base_tree.xpath('//div[@class="poster"]/a/img')[0].get('src')
            if src[0] == '/':
                src = self.base_url + src
            return src
        except IndexError:
            raise GeneralInformationException(f'Cannot locate the main image for {self.audiovisual_record.name}')

    @property
    def name(self):
        try:
            name = self.base_tree.xpath('//div[@class="originalTitle"]/text()')[0]
        except IndexError:
            name = self.base_tree.xpath('//div[@class="title_wrapper"]/h1/text()')[0]
        return re.sub(r'[^\x00-\x7f]', r'', name)

    @property
    def year(self):
        try:
            year_text_results = self.base_tree.xpath(
                '//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div/a[4]/text()'
            )
            if len(year_text_results) == 0:
                year_text_results = self.base_tree.xpath(
                    '//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div/a[3]/text()'
                )
            if len(year_text_results) == 0:
                year_text_results = self.base_tree.xpath(
                    '//*[@id="titleYear"]/a/text()'
                )
            year_text = year_text_results[0]
            result = re.search(r'.*(\d{4}).*', year_text)
            if result:
                return result.group(1)
            else:
                raise IndexError
        except IndexError:
            raise GeneralInformationException(f'Cannot locate the year for {self.audiovisual_record.name}')

    @property
    def writers_directors_stars(self):
        possible_targets = ['director:', 'star:', 'writer:']
        directors = []
        stars = []
        writers = []
        target = None
        for text_found in self.base_tree.xpath('//div[@class="credit_summary_item"]/h4/text()|'
                                               '//div[@class="credit_summary_item"]/a/text()'):
            if are_similar_strings(text_found, 'See full cast & crew'):
                continue
            if are_similar_strings(text_found.lower(), ' more credit'):
                continue
            target_changed = False
            for possible_target in possible_targets:
                if are_similar_strings(text_found, possible_target):
                    target = possible_target
                    target_changed = True
            if target_changed:
                continue

            if target == 'director:':
                directors.append(text_found)
            elif target == 'star:':
                stars.append(text_found)
            elif target == 'writer:':
                writers.append(text_found)

        writers = [Person(name=p) for p in writers]
        directors = [Person(name=p) for p in directors]
        stars = [Person(name=p) for p in stars]
        return writers, directors, stars

    @property
    def genres(self):
        genres = self.base_tree.xpath('//*[@id="title-overview-widget"]/div[1]/div[2]/div/div[2]/div[2]/div'
                                      '/a[contains(@href, "genres")]/text()')
        if len(genres) == 0:
            raise GeneralInformationException(f'Cannot locate the genres for {self.audiovisual_record.name}')
        return [Genre(name=g) for g in genres]

    @property
    def is_a_film(self):
        return len(self.base_tree.xpath('//*[@id="title-episode-widget"]')) == 0

    @property
    def base_tree(self):
        if self._base_tree is not None:
            return self._base_tree
        headers = {'Accept-Language': 'en,es;q=0.9,pt;q=0.8'}
        session = PhantomBrowsingSession(referer='https://www.google.com/', headers=headers)
        try:
            detailed_page = self.audiovisual_record.metadata['detailed_page'][self.source_name]
            href = IMDBGeneralInformation.base_url + detailed_page
        except KeyError:
            # first search for the detailed page link
            name = self.audiovisual_record.name
            name = percent_encoding(name)
            session.get(f'{IMDBGeneralInformation.base_url}/find?ref_=nv_sr_fn&q={name}&s=all')
            response = session.last_response
            tree = html.fromstring(response.content)
            results = tree.xpath('//td[@class="result_text"]/a')
            first_result_node = results[0]
            # this is the detail page link
            href = IMDBGeneralInformation.base_url + first_result_node.get('href')

        session.get(href)
        response = session.last_response
        self._base_tree = html.fromstring(response.content)
        return self._base_tree
