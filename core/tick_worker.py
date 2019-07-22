import functools
import threading
import time
from datetime import datetime
import glob
import os

from core.tools.logs import log_exception
from core.tools.packages import PackageDiscover, ModuleDiscover
from core import robots


class Ticker:
    INTERVALS = {
        '1-minute': {'seconds': 1 * 60, 'functions': []},
        '5-minutes': {'seconds': 5 * 60, 'functions': []},
        '30-minutes': {'seconds': 30 * 60, 'functions': []},
        '60-minutes': {'seconds': 60 * 60, 'functions': []},
        '12-hours': {'seconds': 12 * 60 * 60, 'functions': []},
    }

    @classmethod
    def execute_each(cls, interval='1-minute'):
        def wrapper(func):
            func.interval = interval
            @functools.wraps(func)
            def wrapped(*args):
                return func(*args)
            return wrapped
        return wrapper

    @classmethod
    def _can_acquire_lock(cls, func):
        lock_file = cls._lock_filename(func)
        if os.path.exists(lock_file):
            print(f'Cannot acquire lock {lock_file}')
            return False
        else:
            print(f'Lock {lock_file} acquired')
            open(lock_file, 'w').close()
            return True

    @classmethod
    def _release_lock(cls, func):
        lock_file = cls._lock_filename(func)
        os.remove(lock_file)

    @classmethod
    def _lock_filename(cls, func):
        return '/tmp/.filmstreator.' + func.__module__ + '.' + func.__name__ + '.lock'

    @classmethod
    def release_all_locks(cls):
        """
        When system start up all locks must be released
        """
        for lock_file in glob.glob('/tmp/.filmstreator.*.lock'):
            os.remove(lock_file)

    def _get_applying_intervals(self, ts):
        interval_slugs = []
        for interval_slug, data in Ticker.INTERVALS.items():
            seconds = data['seconds']
            if ts % seconds == 0:
                interval_slugs.append(interval_slug)
        return interval_slugs

    def _execute_tasks(self, ts):
        interval_slugs = self._get_applying_intervals(ts)
        for interval_slug in interval_slugs:
            for function in Ticker.INTERVALS[interval_slug]['functions']:
                if not Ticker._can_acquire_lock(function):
                    continue
                try:
                    thread = threading.Thread(target=Ticker._thread_executed_function, args=[function])
                    thread.start()
                except Exception as e:
                    log_exception(e)

    @classmethod
    def _thread_executed_function(cls, function):
        print(f'Executing function {function}')
        function()
        Ticker._release_lock(function)

    def start(self):
        while True:
            # TODO enhance ticker. Must wait the needed for the next second
            ts = int(datetime.utcnow().timestamp())
            self._execute_tasks(ts)
            time.sleep(1)

    def register_callable(self, function, interval):
        assert interval in Ticker.INTERVALS.keys(), 'Invalid interval provided'
        print(f'Registering {function}')
        self.INTERVALS[interval]['functions'].append(function)

    def autodiscover_robots(self, base_package):
        package_discover = PackageDiscover(base_package)
        for module in package_discover.modules:
            module_discover = ModuleDiscover(module)
            for function in module_discover.functions:
                if hasattr(function, 'interval'):
                    interval = function.interval
                else:
                    continue
                self.register_callable(function, interval)


def start_ticker():
    # on startup we release all locks
    Ticker.release_all_locks()
    ticker = Ticker()
    ticker.autodiscover_robots(robots)
    ticker.start()
