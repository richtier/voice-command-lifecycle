import collections


class AudioBufferBase(collections.deque):
    maxlen = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, maxlen=self.maxlen)

    def get(self) -> bytes:
        return bytes(bytearray(self))

    def popleft_size(self, size: int) -> bytes:
        sliced = bytearray()
        for i in range(size):
            if self:
                sliced.append(self.popleft())
        return bytes(sliced)


class WakewordAudioBuffer(AudioBufferBase):
    """ Store a few seconds of audio"""
    maxlen = 40000


class CommandAudioBuffer(AudioBufferBase):
    """ Store a "infinite" seconds of audio"""
    pass
