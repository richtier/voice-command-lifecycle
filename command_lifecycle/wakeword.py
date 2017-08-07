import abc
import importlib
from typing import Type

from command_lifecycle.buffer import AudioBufferBase


class BaseWakewordDetector(abc.ABC):

    wakeword_library_import_path = abc.abstractproperty()
    import_error_message = abc.abstractproperty()

    def get_wakeword_library(self):
        package_name, name  = self.wakeword_library_import_path.rsplit('.', 1)
        try:
            package_name = importlib.import_module(package_name)
        except ImportError:
            raise ImportError(self.import_error_message)
        return getattr(package_name, name)

    def was_wakeword_uttered(self, buffer: Type[AudioBufferBase]) -> bool:
        raise NotImplementedError()

    def is_talking(self, buffer: Type[AudioBufferBase]) -> bool:
        raise NotImplementedError()


class SnowboyWakewordDetector(BaseWakewordDetector):
    """
    Detect whether a wakeword exists in an audio stream.

    Args:
        sensitivity: decoder sensitivity, a float.
                    The bigger the value, the more sensitive the decoder.
        audio_gain: multiply input volume by this factor.

    """

    import_error_message = 'Cannot import Snowboy. See README.md for help.'
    wakeword_library_import_path = 'snowboy.snowboydetect.SnowboyDetect'

    resource_file = b'snowboy/resources/common.res'
    decoder_model = b'snowboy/resources/snowboy.umdl'
    sensitivity = 0.5
    audio_gain = 1

    def __init__(self):
        SnowboyDetect = self.get_wakeword_library()
        self.detector = SnowboyDetect(
            resource_filename=self.resource_file, model_str=self.decoder_model
        )
        self.detector.SetAudioGain(self.audio_gain)
        self.detector.SetSensitivity(str(self.sensitivity).encode())

    def was_wakeword_uttered(self, buffer: Type[AudioBufferBase]) -> bool:
        # -2 on silence, -1 on error, 0 on voice and >0
        return self.detector.RunDetection(buffer.get()) > 0

    def is_talking(self, buffer: Type[AudioBufferBase]) -> bool:
        return self.detector.RunDetection(buffer.get()) == 0
