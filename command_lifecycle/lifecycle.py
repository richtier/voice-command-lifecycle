from typing import Iterable

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
        self.timeout_manager = self.timeout_manager_class()

    def extend_audio(self, input_audio: Iterable[int]):
        wav_audio = self.audio_converter_class.convert(input_audio)
        self.audio_buffer.extend(wav_audio)
        if self.was_wakeword_uttered():
            self.handle_command_started()
            self.timeout_manager.reset()
        elif self.has_command_finished():
            self.handle_command_finised()
        elif self.is_talking():
            self.timeout_manager.reset()

    def is_talking(self) -> bool:
        return self.audio_detector.is_talking(self.audio_buffer)

    def was_wakeword_uttered(self) -> bool:
        return self.audio_detector.was_wakeword_uttered(self.audio_buffer)

    def has_timedout(self) -> bool:
        return self.timeout_manager.has_timedout()

    def has_command_finished(self) -> bool:
        if not self.is_command_pending:
            return False
        # prevent prematurely finishing the command
        # e.g., user is thinking briefly, or there is pause between wakeword
        # being uttered and the command being said.
        return not self.is_talking() and self.has_timedout()

    def handle_command_started(self):
        self.is_command_pending = True
        self.audio_buffer = self.command_audio_buffer_class()

    def handle_command_finised(self):
        self.is_command_pending = False
        self.audio_buffer = self.wakeword_audio_buffer_class()
