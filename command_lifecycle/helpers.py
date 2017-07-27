from array import array
import audioop
import struct


class NoOperationConverter:
    """If the inbound audio is already wav then no operation needed."""
    @classmethod
    def convert(cls, wav_bytes):
        return wav_bytes


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
    def convert(cls, raw_floats):
        left_channel, right_channel = audioop.ratecv(
            cls.float_to_pcm(raw_floats),
            cls.sample_width,
            cls.audio_channels,
            cls.webaudio_sample_rate,  # input rate
            cls.wav_sample_rate,  # output rate
            None,  # state
        )
        return left_channel

    @classmethod
    def float_to_pcm(cls, raw_floats):
        floats = array('f', raw_floats)
        # powerful microphones can output samples out of range (<-1.0, >1.0).
        floats = (filter(lambda x: x >= -1.0 and x <= 1.0, floats))
        samples = [int(sample * 32767) for sample in floats]
        return struct.pack("<%dh" % len(samples), *samples)
