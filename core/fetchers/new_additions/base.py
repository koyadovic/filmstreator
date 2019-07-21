from core.tools.browsing import PhantomBrowsingSession

from datetime import datetime
from typing import List
from lxml import html
import abc


class AbstractNewAdditions(metaclass=abc.ABCMeta):
    all_names_xpath = None
    base_url = None

    def get(self, from_date: datetime, to_date: datetime) -> List[str]:
        session = PhantomBrowsingSession(referer=self.base_url + '/')
        session.get(self.get_search_url(from_date, to_date), timeout=30)
        response = session.last_response
        if not self.results_found(response.content):
            return []
        names = self.extract_all_names(response.content)
        return names

    def extract_all_names(self, page):
        tree = html.fromstring(page)
        names = tree.xpath(self.all_names_xpath)
        return names

    def results_found(self, page):
        raise NotImplementedError

    def get_search_url(self, from_date: datetime, to_date: datetime):
        raise NotImplementedError
