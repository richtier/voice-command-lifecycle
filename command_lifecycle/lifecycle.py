from command_lifecycle import buffer, helpers, timeout, wakeword


class BaseAudioLifecycle:
    audio_buffer = None
    audio_converter_class = helpers.NoOperationConverter
    audio_detector_class = wakeword.SnowboyWakewordDetector
    command_audio_buffer_class = buffer.CommandAudioBuffer
    is_command_pending = False
    wakeword_audio_buffer_class = buffer.WakewordAudioBuffer
    to_audio_file = helpers.LifeCycleFileLike
    timeout_manager_class = timeout.MediumTimeoutManager

    def __init__(self):
        self.audio_buffer = self.wakeword_audio_buffer_class()
        self.audio_detector = self.audio_detector_class()
        self.timeout_manager = self.timeout_manager_class(
            function=self.handle_command_finised
        )

    def extend_audio(self, input_audio):
        wav_audio = self.audio_converter_class.convert(input_audio)
        self.audio_buffer.extend(wav_audio)
        if self.is_command_pending and self.is_talking():
            self.timeout_manager.reset()
        else:
            wakeword_name = self.get_uttered_wakeword_name()
            if wakeword_name:
                self.handle_command_started(wakeword_name=wakeword_name)

    def is_talking(self):
        return self.audio_detector.is_talking(self.audio_buffer)

    def get_uttered_wakeword_name(self):
        return self.audio_detector.get_uttered_wakeword_name(self.audio_buffer)

    def handle_command_started(self, wakeword_name):
        self.timeout_manager.reset(start=True)
        self.is_command_pending = True
        self.audio_buffer = self.command_audio_buffer_class()

    def handle_command_finised(self):
        self.is_command_pending = False
        self.audio_buffer = self.wakeword_audio_buffer_class()
