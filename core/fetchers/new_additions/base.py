from datetime import datetime
from typing import List
import abc


class AbstractNewAdditions(metaclass=abc.ABCMeta):

    def get(self, from_date: datetime, to_date: datetime) -> List[str]:
        raise NotImplementedError
