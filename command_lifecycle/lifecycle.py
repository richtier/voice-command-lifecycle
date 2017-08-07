from datetime import datetime, timedelta
from typing import Iterable

from command_lifecycle import buffer, helpers, wakeword


class BaseAudioLifecycle:
    audio_buffer = None
    audio_converter_class = helpers.NoOperationConverter
    audio_detector_class = wakeword.SnowboyWakewordDetector
    command_audio_buffer_class = buffer.CommandAudioBuffer
    command_timeout_time = None
    is_command_pending = False
    wakeword_audio_buffer_class = buffer.WakewordAudioBuffer

    def __init__(self):
        self.audio_buffer = self.wakeword_audio_buffer_class()
        self.audio_detector = self.audio_detector_class()

    def extend_audio(self, input_audio: Iterable[int]):
        wav_audio = self.audio_converter_class.convert(input_audio)
        self.audio_buffer.extend(wav_audio)
        if self.was_wakeword_uttered():
            self.handle_command_started()
        elif self.has_command_finished():
            self.handle_command_finised()

    def is_quiet(self) -> bool:
        return not self.audio_detector.is_talking(self.audio_buffer)

    def was_wakeword_uttered(self) -> bool:
        return self.audio_detector.was_wakeword_uttered(self.audio_buffer)

    def handle_command_started(self):
        print('expecting command')
        self.is_command_pending = True
        self.command_timeout_time = datetime.utcnow() + timedelta(seconds=3)
        self.audio_buffer = self.command_audio_buffer_class()

    def handle_command_finised(self):
        self.is_command_pending = False
        self.command_timeout_time = None
        self.audio_buffer = self.wakeword_audio_buffer_class()

    def has_command_finished(self) -> bool:
        if not self.is_command_pending:
            return False
        # prevent prematurely finishing the command
        # e.g., user is thinking briefly, or there is pause between wakeword
        # being uttered and the command being said.
        return self.is_quiet() and self.has_command_timedout()

    def has_command_timedout(self) -> bool:
        return datetime.utcnow() >= self.command_timeout_time
