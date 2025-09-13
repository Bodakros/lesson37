import random
from datetime import timedelta as td, datetime

from tzlocal import get_localzone


def now_local():
    datetime_kyiv = datetime.now(get_localzone())
    return datetime_kyiv


class Timer:
    def __init__(self,
                 check_interval_min: td = td(),
                 check_interval_max: td = None,
                 initial_passed: td = td(seconds=0)):
        if check_interval_max is None:
            check_interval_max = check_interval_min

        self.start_time = now_local() - check_interval_max
        self.interval_mid = None
        self.interval_variation_mcs = None
        self.initial_passed = None
        self.actual_interval = None
        self.initial_passed = initial_passed
        self.elapsed = td()

        self.update_interval(check_interval_min, check_interval_max)

    def generate_new_actual_interval(self):
        if self.interval_variation_mcs == 0:
            return self.interval_mid
        new_interval_variation_mcs = random.randrange(-self.interval_variation_mcs, self.interval_variation_mcs)
        return self.interval_mid + td(microseconds=new_interval_variation_mcs)

    def start(self):
        self.start_time = now_local() - self.initial_passed
        self.initial_passed = td()
        self.actual_interval = self.generate_new_actual_interval()
        return self

    def try_restart_expired(self):
        self.elapsed = now_local() - self.start_time
        is_expired = self.elapsed > self.actual_interval
        if is_expired:
            self.start()
        return is_expired

    def reset(self, initial_passed: td = td()):
        self.initial_passed = initial_passed
        self.start()

    def update_interval(self, check_interval_min: td = td(seconds=0),
                        check_interval_max: td = None):
        if check_interval_max is None:
            check_interval_max = check_interval_min
        self.interval_mid = (check_interval_min + check_interval_max) // 2
        self.interval_variation_mcs = abs(check_interval_max.microseconds - check_interval_min.microseconds) // 2
        self.actual_interval = self.generate_new_actual_interval()

        return self

    @property
    def already_passed(self) -> td:
        return now_local() - self.start_time

    def is_expired(self):
        self.elapsed = now_local() - self.start_time
        is_expired = self.elapsed > self.actual_interval
        return is_expired
