import asyncio
from datetime import datetime


class Ticker:
    INTERVALS = {
        '1-minute': {
            'seconds': 1 * 60,
            'functions': []
        },
        '5-minute': {
            'seconds': 5 * 60,
            'functions': []
        },
        '30-minute': {
            'seconds': 30 * 60,
            'functions': []
        },
        '60-minute': {
            'seconds': 60 * 60,
            'functions': []
        },
        '12-hours': {
            'seconds': 12 * 60 * 60,
            'functions': []
        },
    }

    def register_function(self, function, interval):
        assert interval in Ticker.INTERVALS.keys(), 'Invalid interval provided'
        self.INTERVALS[interval]['functions'].append(function)

    async def _get_applying_intervals(self, ts):
        interval_slugs = []
        for interval_slug, data in Ticker.INTERVALS.items():
            seconds = data['seconds']
            if ts % seconds == 0:
                interval_slugs.append(interval_slug)
        return interval_slugs

    async def _execute_tasks(self, ts):
        interval_slugs = await self._get_applying_intervals(ts)
        for interval_slug in interval_slugs:
            for function in Ticker.INTERVALS[interval_slug]['functions']:
                function()

    async def start(self):
        while True:
            ts = int(datetime.utcnow().timestamp())
            await self._execute_tasks(ts)
            await asyncio.sleep(1)


ticker = Ticker()


"""
TODO register here all robot callables
ticker.register_function(function, '1-minute')
"""


await ticker.start()
