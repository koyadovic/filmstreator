from core.model.audiovisual import AudiovisualRecord
from core.tools.browsing import PhantomBrowsingSession

from datetime import datetime
from typing import List
from lxml import html
import abc


class AbstractNewAdditions(metaclass=abc.ABCMeta):
    all_names_xpath = None
    all_detail_pages_xpath = None
    base_url = None
    source_name = None

    def get(self, from_date: datetime, to_date: datetime) -> List[AudiovisualRecord]:
        headers = {'Accept-Language': 'en,es;q=0.9,pt;q=0.8'}
        session = PhantomBrowsingSession(referer=self.base_url + '/', headers=headers)
        session.get(self.get_search_url(from_date, to_date), timeout=30)
        response = session.last_response
        if response is None or not self.results_found(response.content):
            return []
        audiovisual_records = []
        names = self.extract_all_names(response.content)
        links = self.extract_all_detail_pages(response.content)
        for n, name in enumerate(names):
            link = links[n]
            audiovisual_record = AudiovisualRecord(name=name)
            self._prepare_metadata_dict(audiovisual_record)
            audiovisual_record.metadata['detailed_page'][self.source_name] = link
            audiovisual_records.append(audiovisual_record)

        return audiovisual_records

    def extract_all_names(self, page):
        tree = html.fromstring(page)
        names = tree.xpath(self.all_names_xpath)
        return names

    def extract_all_detail_pages(self, page):
        tree = html.fromstring(page)
        links = tree.xpath(self.all_detail_pages_xpath)
        return links

    def results_found(self, page):
        raise NotImplementedError

    def get_search_url(self, from_date: datetime, to_date: datetime):
        raise NotImplementedError

    def _prepare_metadata_dict(self, audiovisual_record):
        if 'detailed_page' not in audiovisual_record.metadata:
            audiovisual_record.metadata['detailed_page'] = {}
        if self.source_name not in audiovisual_record.metadata['detailed_page']:
            audiovisual_record.metadata['detailed_page'][self.source_name] = ''
