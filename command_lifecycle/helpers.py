from array import array
import audioop
import struct


class NoOperationConverter:
    """If the inbound audio is already wave bytes then no operation needed."""
    @classmethod
    def convert(cls, samples):
        return samples


class WavIntSamplestoWavConverter:
    """
    Convert list of integers to wav.

    """
    @classmethod
    def convert(cls, samples):
        return struct.pack("<%dh" % len(samples), *samples)


class WebAudioToWavConverter:
    """
    Convert webaudio from web browsers to wav.

    The raw values captured from the Web Audio API are 32-bit Floating Point,
    between -1 and 1 (per the specification).

    Alexa requires samples in 16-bit PCM range between -32768 and +32767
    (16-bit signed integer), little endian.

    """

    webaudio_sample_rate = 44100
    wav_sample_rate = 16000
    sample_width = 2
    audio_channels = 1

    @classmethod
    def convert(cls, samples):
        left_channel, right_channel = audioop.ratecv(
            cls.float_to_pcm(samples),
            cls.sample_width,
            cls.audio_channels,
            cls.webaudio_sample_rate,  # input rate
            cls.wav_sample_rate,  # output rate
            None,  # state
        )
        return left_channel

    @classmethod
    def float_to_pcm(cls, samples):
        floats = array('f', samples)
        # powerful microphones can output samples out of range (<-1.0, >1.0).
        floats = (filter(lambda x: x >= -1.0 and x <= 1.0, floats))
        samples = [int(sample * 32767) for sample in floats]
        return struct.pack("<%dh" % len(samples), *samples)


class LifeCycleFileLike:
    def __init__(self, lifecycle):
        self.lifecycle = lifecycle

    def read(self, size):
        return self.lifecycle.audio_buffer.popleft_size(size)

    def __len__(self):
        # when length == 0 the uploader will close the request. If the stream
        # has all the data popped from it, but there is more to be written to
        # it then make the uploader wait by making the uploader think there is
        # data available.
        if self.lifecycle.is_command_pending:
            return 1025
        return len(self.lifecycle.audio_buffer)
