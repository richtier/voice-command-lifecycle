from typing import Union, Type
import os

from command_lifecycle.buffer import AudioBufferBase
from command_lifecycle.snowboy import snowboydetect


Numeric = Union[float, int]


class WakewordDetector:
    """
    Detect whether a wakeword exists in an audio stream.

    Args:
        sensitivity: decoder sensitivity, a float.
                    The bigger the value, the more sensitive the decoder.
        audio_gain: multiply input volume by this factor.

    """

    top_dir = os.path.dirname(os.path.abspath(__file__))
    resource_file = os.path.join(top_dir, "./snowboy/resources/common.res")
    decoder_model = os.path.join(top_dir, "./snowboy/resources/snowboy.umdl")

    def __init__(self, sensitivity: Numeric=0.5, audio_gain: Numeric=1):
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=self.resource_file.encode(),
            model_str=self.decoder_model.encode()
        )
        self.detector.SetAudioGain(audio_gain)
        self.detector.SetSensitivity(str(sensitivity).encode())

    def was_wakeword_uttered(self, buffer: Type[AudioBufferBase]) -> bool:
        # -2 on silence, -1 on error, 0 on voice and >0
        return self.detector.RunDetection(buffer.get()) > 0

    def is_talking(self, buffer: Type[AudioBufferBase]) -> bool:
        return self.detector.RunDetection(buffer.get()) == 0
