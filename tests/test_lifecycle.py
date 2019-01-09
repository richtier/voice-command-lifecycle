from unittest.mock import call, Mock, patch
import wave

import pytest
from resettabletimer import FakeTimer

from command_lifecycle import BaseAudioLifecycle, helpers


class FakeTimeoutManager(FakeTimer):
    allowed_silent_seconds = 1

    def __init__(self, function):
        super().__init__(time=self.allowed_silent_seconds, function=function)

    def reset(self, start=False):
        if start:
            self.start()


class SimpleAudioLifecycle(BaseAudioLifecycle):
    timeout_manager_class = FakeTimeoutManager

    def __init__(self, *args, **kwargs):
        patch.object(
            self, 'handle_command_started',
            wraps=self.handle_command_started
        ).start()
        patch.object(
            self, 'handle_command_finised',
            wraps=self.handle_command_finised
        ).start()
        super().__init__(*args, **kwargs)


@pytest.fixture
def lifecycle():
    return SimpleAudioLifecycle()


@pytest.mark.parametrize("extend_byte_payloads,expected", [
    [[b'one'], b'one'],
    [[b'two|', b'three'], b'two|three'],
    [[b'four|', b'five|', b'six'], b'four|five|six']
])
def test_extend_audio_extends_audio_buffer(extend_byte_payloads, expected):
    class AudioLifecycle(BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)

    lifecycle = AudioLifecycle()

    for wav_bytes in extend_byte_payloads:
        lifecycle.extend_audio(wav_bytes)

    assert lifecycle.audio_buffer.get() == expected


@pytest.mark.parametrize("wakeword_name,call_count", [['ALEXA', 1], [None, 0]])
def test_extend_audio_wakeword_uttered_handled(wakeword_name, call_count):
    class AudioLifecycle(BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=wakeword_name)
        handle_command_started = Mock()

    lifecycle = AudioLifecycle()

    lifecycle.extend_audio(b'one')

    assert lifecycle.handle_command_started.call_count == call_count


@pytest.mark.parametrize("has_finished,call_count", [[True, 1], [False, 0]])
def test_extend_audio_command_finished_handled(has_finished, call_count):
    class AudioLifecycle(BaseAudioLifecycle):
        handle_command_finised = Mock()
        get_uttered_wakeword_name = Mock(return_value='ALEXA')
        timeout_manager_class = FakeTimeoutManager

    lifecycle = AudioLifecycle()

    lifecycle.extend_audio(b'one')

    if has_finished:
        lifecycle.timeout_manager.pass_time(
            lifecycle.timeout_manager.allowed_silent_seconds
        )

    assert lifecycle.handle_command_finised.call_count == call_count


def test_handle_command_started_sets_state():
    class AudioLifecycle(SimpleAudioLifecycle):
        timeout_manager_class = Mock()

    lifecycle = AudioLifecycle()

    lifecycle.handle_command_started('ALEXA')

    assert lifecycle.timeout_manager.reset.call_count == 1
    assert lifecycle.timeout_manager.reset.call_args == call(start=True)

    assert lifecycle.is_command_pending is True
    assert isinstance(
        lifecycle.audio_buffer, SimpleAudioLifecycle.command_audio_buffer_class
    )


def test_handle_command_finised_sets_state(lifecycle):
    lifecycle.handle_command_finised()

    assert lifecycle.is_command_pending is False
    assert isinstance(
        lifecycle.audio_buffer,
        SimpleAudioLifecycle.wakeword_audio_buffer_class
    )


def test_default_audio_converter(lifecycle):
    expected = helpers.NoOperationConverter

    assert lifecycle.audio_converter_class == expected


def test_default_audio_explicit():
    class AudioLifecycle(BaseAudioLifecycle):
        audio_converter_class = helpers.WebAudioToWavConverter

    lifecycle = AudioLifecycle()
    expected = helpers.WebAudioToWavConverter

    assert lifecycle.audio_converter_class == expected


def test_extend_audio_converts_to_wav():
    class AudioLifecycle(BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)
        audio_converter_class = Mock(convert=Mock(return_value='return-value'))
        wakeword_audio_buffer_class = Mock

    lifecycle = AudioLifecycle()
    lifecycle.extend_audio(b'1234')

    assert lifecycle.audio_converter_class.convert.call_count == 1
    assert lifecycle.audio_converter_class.convert.call_args == call(b'1234')
    assert lifecycle.audio_buffer.extend.call_count == 1
    assert lifecycle.audio_buffer.extend.call_args == call('return-value')


def test_to_lifecycle():
    class AudioLifecycle(BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)

    lifecycle = AudioLifecycle()
    lifecycle.extend_audio(b'1234')

    audio_file = lifecycle.to_audio_file(lifecycle)
    assert isinstance(audio_file, helpers.LifeCycleFileLike)
    assert audio_file.lifecycle == lifecycle


def test_e2e_snowboy_snowboy_executes_callbacks(enable_snowboy, lifecycle):
    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0

    with wave.open('./tests/resources/alexa_what_time_is_it.wav', 'rb') as f:
        while f.tell() < f.getnframes():
            lifecycle.extend_audio(f.readframes(1024))

    assert lifecycle.handle_command_started.call_count == 1
    # finished not called yet: the command has not timed out yet
    assert lifecycle.handle_command_finised.call_count == 0

    lifecycle.timeout_manager.pass_time(
        lifecycle.timeout_manager.allowed_silent_seconds + 1
    )

    assert lifecycle.handle_command_finised.call_count == 1


def test_e2e_no_wakeword(enable_snowboy, lifecycle):
    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0

    with wave.open('./tests/resources/jim_what_time_is_it.wav', 'rb') as f:
        while f.tell() < f.getnframes():
            lifecycle.extend_audio(f.readframes(1024))

    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0
