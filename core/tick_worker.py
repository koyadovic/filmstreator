import asyncio
import glob
import importlib
import inspect
import os
import pkgutil
from datetime import datetime

from sentry_sdk import capture_exception

from core import robots


class Ticker:
    INTERVALS = {
        '1-minute': {'seconds': 1 * 60, 'functions': []},
        '5-minute': {'seconds': 5 * 60, 'functions': []},
        '30-minute': {'seconds': 30 * 60, 'functions': []},
        '60-minute': {'seconds': 60 * 60, 'functions': []},
        '12-hours': {'seconds': 12 * 60 * 60, 'functions': []},
    }

    @classmethod
    def _can_acquire_lock(cls, func):
        lock_file = cls._lock_filename(func)
        if os.path.exists(lock_file):
            return False
        else:
            open(lock_file, 'w').close()
            return True

    @classmethod
    def _release_lock(cls, func):
        lock_file = cls._lock_filename(func)
        os.remove(lock_file)

    @classmethod
    def _lock_filename(cls, func):
        return '/tmp/.' + func.__module__ + '.' + func.__name__ + '.lock'

    @classmethod
    def release_all_locks(cls):
        """
        When system start up all locks must be released
        """
        for lock_file in glob.glob('/tmp/.*.lock'):
            os.remove(lock_file)

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
                if not Ticker._can_acquire_lock(function):
                    continue
                try:
                    await function()
                except Exception as e:
                    capture_exception(e)
                finally:
                    Ticker._release_lock(function)

    async def start(self):
        while True:
            ts = int(datetime.utcnow().timestamp())
            await self._execute_tasks(ts)
            await asyncio.sleep(1)

    def register_function(self, function, interval):
        assert interval in Ticker.INTERVALS.keys(), 'Invalid interval provided'
        self.INTERVALS[interval]['functions'].append(function)

    def autodiscover_robots(self, base_package):
        for importer, modname, ispkg in pkgutil.iter_modules(base_package.__path__):
            if ispkg:
                continue
            module_name = base_package.__name__ + '.' + modname
            module = importlib.import_module(module_name)
            functions = inspect.getmembers(module, inspect.isfunction)
            for function_tuple in functions:
                function = function_tuple[1]
                if inspect.iscoroutinefunction(function):
                    if hasattr(function, 'interval'):
                        interval = function.interval
                    else:
                        interval = '1-minute'
                    self.register_function(function, interval)


def start_ticker():
    # on startup we release all locks
    Ticker.release_all_locks()
    ticker = Ticker()
    ticker.autodiscover_robots(robots)
    asyncio.run(ticker.start())
