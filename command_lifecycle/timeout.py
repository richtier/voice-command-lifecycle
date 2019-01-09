import abc

from resettabletimer import ResettableTimer


class BaseTimeoutManager(abc.ABC, ResettableTimer):

    @property
    @abc.abstractmethod
    def allowed_silent_seconds(self):
        return 0

    def __init__(self, function):
        super().__init__(time=self.allowed_silent_seconds, function=function)


class ShortTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 1


class MediumTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 2


class LongTimeoutManager(BaseTimeoutManager):
    allowed_silent_seconds = 3
