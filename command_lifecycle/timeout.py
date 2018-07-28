import abc
from datetime import datetime


class BaseTimeoutManager(abc.ABC):
    allowed_silent_seconds = abc.abstractproperty()

    def reset(self):
        self.silence_started_time = datetime.utcnow()

    def has_timedout(self) -> bool:
        return self.remaining_silent_seconds <= 0

    @property
    def elapsed_silent_seconds(self) -> int:
        if self.silence_started_time is None:
            raise ValueError('reset must be called before this method')
        return (datetime.utcnow() - self.silence_started_time).total_seconds()

    @property
    def remaining_silent_seconds(self) -> int:
        return self.allowed_silent_seconds - self.elapsed_silent_seconds


class ShortTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 1


class MediumTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 2


class LongTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 3
