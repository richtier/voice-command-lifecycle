from datetime import datetime
from unittest.mock import call, Mock

from freezegun import freeze_time
import pytest

from command_lifecycle.lifecycle import BaseAudioLifecycle
from command_lifecycle import helpers


class SimpleAudioLifecycle(BaseAudioLifecycle):
    pass


@pytest.mark.parametrize("extend_byte_payloads,expected", [
    [[b'one'], b'one'],
    [[b'two|', b'three'], b'two|three'],
    [[b'four|', b'five|', b'six'], b'four|five|six']
])
def test_extend_audio_extends_audio_buffer(extend_byte_payloads, expected):
    lifecycle = SimpleAudioLifecycle()

    for wav_bytes in extend_byte_payloads:
        lifecycle.extend_audio(wav_bytes)

    assert lifecycle.audio_buffer.get() == expected


@pytest.mark.parametrize("was_uttered,call_count", [[True, 1], [False, 0]])
def test_extend_audio_wakeword_uttered_handled(was_uttered, call_count):
    class AudioLifecycle(BaseAudioLifecycle):
        was_wakeword_uttered = Mock(return_value=was_uttered)
        handle_command_started = Mock()

    lifecycle = AudioLifecycle()

    lifecycle.extend_audio(b'one')

    assert lifecycle.handle_command_started.call_count == call_count


@pytest.mark.parametrize("has_finished,call_count", [[True, 1], [False, 0]])
def test_extend_audio_command_finished_handled(has_finished, call_count):
    class AudioLifecycle(BaseAudioLifecycle):
        has_command_finished = Mock(return_value=has_finished)
        handle_command_finised = Mock()

    lifecycle = AudioLifecycle()

    lifecycle.extend_audio(b'one')

    assert lifecycle.handle_command_finised.call_count == call_count


@freeze_time('2012-01-14 12:00:00')
def test_handle_command_started_sets_state():
    lifecycle = SimpleAudioLifecycle()

    lifecycle.handle_command_started()

    assert lifecycle.is_command_pending is True
    assert lifecycle.command_timeout_time.isoformat() == '2012-01-14T12:00:03'


def test_handle_command_finised_sets_state():
    lifecycle = SimpleAudioLifecycle()

    lifecycle.handle_command_finised()

    assert lifecycle.is_command_pending is False
    assert lifecycle.command_timeout_time is None


@pytest.mark.parametrize("expecting_command,quiet,has_timedout", [
    (True,  False, False),
    (True,  False, True),
    (True,  True,  False),
    (False, False, True),
    (False, False, False),
    (False, True,  False),
    (False, True,  True),
])
def test_has_command_finished_false(expecting_command, quiet, has_timedout):
    class AudioLifecycle(BaseAudioLifecycle):
        is_command_pending = expecting_command
        is_quiet = Mock(return_value=quiet)
        has_command_timedout = Mock(return_value=has_timedout)

    lifecycle = AudioLifecycle()
    assert lifecycle.has_command_finished() is False


def test_has_command_finished_true():

    class AudioLifecycle(BaseAudioLifecycle):
        is_command_pending = True
        is_quiet = Mock(return_value=True)
        has_command_timedout = Mock(return_value=True)

    lifecycle = AudioLifecycle()
    assert lifecycle.has_command_finished() is True


@freeze_time('2012-01-14 12:00:04')
def has_has_command_timedout_true():
    lifecycle = SimpleAudioLifecycle()

    lifecycle.command_timeout_time = datetime(2012, 1, 14, 12, 0, 0)

    assert lifecycle.has_command_timedout() is True


@freeze_time('2012-01-14 12:00:03')
def has_has_command_timedout_false():
    lifecycle = SimpleAudioLifecycle()
    lifecycle.audio_buffer.handle_short_audio()

    lifecycle.command_timeout_time = datetime(2012, 1, 14, 12, 0, 0)

    assert lifecycle.has_command_timedout() is False


def test_default_audio_converter():
    lifecycle = SimpleAudioLifecycle()
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
        was_wakeword_uttered = Mock(return_value=False)
        has_command_finished = Mock(return_value=False)
        audio_converter_class = Mock(convert=Mock(return_value='return-value'))
        wakeword_audio_buffer_class = Mock

    lifecycle = AudioLifecycle()
    lifecycle.extend_audio(b'1234')

    assert lifecycle.audio_converter_class.convert.call_count == 1
    assert lifecycle.audio_converter_class.convert.call_args == call(b'1234')
    assert lifecycle.audio_buffer.extend.call_count == 1
    assert lifecycle.audio_buffer.extend.call_args == call('return-value')
