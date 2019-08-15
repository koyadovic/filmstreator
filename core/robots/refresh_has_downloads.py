from datetime import datetime, timezone, timedelta

from core.model.audiovisual import AudiovisualRecord
from core.model.searches import Search, Condition
from core.robots.downloads import _check_has_downloads
from core.tick_worker import Ticker


@Ticker.execute_each(interval='60-minutes')
def do_the_refresh():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    records = (
        Search.Builder
        .new_search(AudiovisualRecord)
        .add_condition(Condition('created_date', Condition.GREAT_OR_EQUAL_THAN, now - timedelta(days=2))).search()
    )
    for record in records:
        _check_has_downloads(record)
