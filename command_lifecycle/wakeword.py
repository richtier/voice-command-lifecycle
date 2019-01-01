import abc
import importlib


class BaseWakewordDetector(abc.ABC):

    wakeword_library_import_path = abc.abstractproperty()
    import_error_message = abc.abstractproperty()

    def get_wakeword_library(self):
        package_name, name = self.wakeword_library_import_path.rsplit('.', 1)
        try:
            package_name = importlib.import_module(package_name)
        except ImportError:
            raise ImportError(self.import_error_message)
        return getattr(package_name, name)

    @abc.abstractmethod
    def is_talking(self, buffer):
        return False

    @abc.abstractmethod
    def get_uttered_wakeword_name(self):
        return None


class SnowboyWakewordDetector(BaseWakewordDetector):
    """
    Use snowboy to detect whether a wakeword exists in an audio stream.

    """

    ALEXA = 'ALEXA'

    import_error_message = 'Cannot import Snowboy. See README.md for help.'
    wakeword_library_import_path = 'snowboy.snowboydetect.SnowboyDetect'
    resource_file = b'snowboy/resources/common.res'
    decoder_models = [
        {
            'name': ALEXA,
            'model': b'snowboy/resources/alexa.umdl',
            'sensitivity': b'0.5',
        }
    ]
    audio_gain = 1

    def __init__(self):
        SnowboyDetect = self.get_wakeword_library()
        self.detector = SnowboyDetect(
            resource_filename=self.resource_file,
            model_str=b','.join([i['model'] for i in self.decoder_models]),
        )
        self.detector.SetAudioGain(self.audio_gain)
        self.detector.SetSensitivity(
            b','.join([i['sensitivity'] for i in self.decoder_models])
        )

    def is_talking(self, buffer):
        return self.detector.RunDetection(buffer.get()) == 0

    def get_uttered_wakeword_name(self, buffer):
        index = self.detector.RunDetection(buffer.get())
        if index > 0:
            return self.decoder_models[index - 1]['name']
