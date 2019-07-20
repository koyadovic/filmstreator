from core.fetchers.new_additions.base import AbstractNewAdditions
from datetime import datetime
from typing import List


class IMDBNewAdditions(AbstractNewAdditions):
    def get(self, from_date: datetime, to_date: datetime) -> List[str]:
        pass
