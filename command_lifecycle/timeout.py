import abc
from datetime import datetime, timedelta


class BaseTimeoutManager(abc.ABC):
    timeout_time = None
    timeout_seconds = abc.abstractproperty()

    def start(self):
        delta = timedelta(seconds=self.timeout_seconds)
        self.timeout_time = datetime.utcnow() + delta

    def stop(self):
        self.timeout_time = None

    def has_timedout(self) -> bool:
        return datetime.utcnow() >= self.timeout_time


class ImmediateTimeoutManager(BaseTimeoutManager):
    timeout_seconds = 0


class ShortTimeoutManager(BaseTimeoutManager):
    timeout_seconds = 1


class MediumTimeoutManager(BaseTimeoutManager):
    timeout_seconds = 2


class LongTimeoutManager(BaseTimeoutManager):
    timeout_seconds = 4
