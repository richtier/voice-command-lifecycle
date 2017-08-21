import abc


class BaseTimeoutManager(abc.ABC):
    allowed_silent_frames = abc.abstractproperty()
    elapsed_silent_frames = 0

    def increment(self):
        self.elapsed_silent_frames += 1

    def reset(self):
        self.elapsed_silent_frames = 0

    def has_timedout(self) -> bool:
        return self.elapsed_silent_frames >= self.allowed_silent_frames

    @property
    def remaining_silent_frames(self):
        return self.allowed_silent_frames - self.elapsed_silent_frames

class ShortTimeoutManager(BaseTimeoutManager):
    allowed_silent_frames = 10


class MediumTimeoutManager(BaseTimeoutManager):
    allowed_silent_frames = 15


class LongTimeoutManager(BaseTimeoutManager):
    allowed_silent_frames = 20
