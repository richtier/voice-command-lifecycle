from unittest.mock import call, Mock, patch
import wave

from freezegun import freeze_time
import pytest

from command_lifecycle import BaseAudioLifecycle, helpers, timeout


class SimpleAudioLifecycle(BaseAudioLifecycle):
    pass


@pytest.mark.parametrize("extend_byte_payloads,expected", [
    [[b'one'], b'one'],
    [[b'two|', b'three'], b'two|three'],
    [[b'four|', b'five|', b'six'], b'four|five|six']
])
def test_extend_audio_extends_audio_buffer(extend_byte_payloads, expected):
    class AudioLifecycle(BaseAudioLifecycle):
        was_wakeword_uttered = Mock(return_value=False)

    lifecycle = AudioLifecycle()

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
        was_wakeword_uttered = Mock(return_value=False)
    lifecycle = AudioLifecycle()

    lifecycle.extend_audio(b'one')

    assert lifecycle.handle_command_finised.call_count == call_count


def test_handle_command_started_sets_state():
    lifecycle = SimpleAudioLifecycle()

    lifecycle.handle_command_started()

    assert lifecycle.is_command_pending is True
    assert isinstance(
        lifecycle.audio_buffer, SimpleAudioLifecycle.command_audio_buffer_class
    )


def test_handle_command_finised_sets_state():
    lifecycle = SimpleAudioLifecycle()

    lifecycle.handle_command_finised()

    assert lifecycle.is_command_pending is False
    assert isinstance(
        lifecycle.audio_buffer,
        SimpleAudioLifecycle.wakeword_audio_buffer_class
    )

@pytest.mark.parametrize("expecting_command,talking,has_timedout", [
    (True,  True,  False),
    (True,  True,  True),
    (True,  False, False),
    (False, True,  True),
    (False, True,  False),
    (False, False, False),
    (False, False, True),
])
def test_has_command_finished_false(expecting_command, talking, has_timedout):

    class AudioLifecycle(BaseAudioLifecycle):
        is_command_pending = expecting_command
        is_talking = Mock(return_value=talking)

        @classmethod
        def timeout_manager_class(cls):
            if has_timedout:
                return timeout.ImmediateTimeoutManager()
            return timeout.ShortTimeoutManager()

    lifecycle = AudioLifecycle()
    lifecycle.timeout_manager.start()

    assert lifecycle.has_command_finished() is False


def test_has_command_finished_true():

    class AudioLifecycle(BaseAudioLifecycle):
        is_command_pending = True
        is_talking = Mock(return_value=False)
        timeout_manager_class = timeout.ImmediateTimeoutManager

    lifecycle = AudioLifecycle()
    lifecycle.timeout_manager.start()

    assert lifecycle.has_command_finished() is True


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


def test_to_lifecycle():
    class AudioLifecycle(BaseAudioLifecycle):
        was_wakeword_uttered = Mock(return_value=False)

    lifecycle = AudioLifecycle()
    lifecycle.extend_audio(b'1234')

    audio_file = lifecycle.to_audio_file(lifecycle)
    assert isinstance(audio_file, helpers.LifeCycleFileLike)
    assert audio_file.lifecycle == lifecycle


class MockCallbackMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        patch.object(
            self, 'handle_command_started',
            wraps=self.handle_command_started
        ).start()
        patch.object(
            self, 'handle_command_finised',
            wraps=self.handle_command_finised
        ).start()


def test_e2e_snowboy_snowboy_executes_callbacks(enable_snowboy):
    class AudioLifecycle(MockCallbackMixin, BaseAudioLifecycle):
        timeout_manager_class = timeout.ImmediateTimeoutManager

    lifecycle = AudioLifecycle()

    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0

    with wave.open('./tests/resources/alexa_what_time_is_it.wav', 'rb') as f:
        for i in range(int(f.getnframes()/1024)):
            frame = f.readframes(1024)
            lifecycle.extend_audio(frame)

    assert lifecycle.handle_command_started.call_count == 1
    assert lifecycle.handle_command_finised.call_count == 1


def test_e2e_snowboy_snowboy_executes_callbacks_with_timeout(enable_snowboy):
    class AudioLifecycle(MockCallbackMixin, BaseAudioLifecycle):
        timeout_manager_class = timeout.ShortTimeoutManager

    lifecycle = AudioLifecycle()

    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0

    with wave.open('./tests/resources/alexa_what_time_is_it.wav', 'rb') as f:
        for i in range(int(f.getnframes()/1024)):
            frame = f.readframes(1024)
            lifecycle.extend_audio(frame)

    assert lifecycle.handle_command_started.call_count == 1
    # finished not called yet: the command has not timedout yet
    assert lifecycle.handle_command_finised.call_count == 0

    # adding some silence to the end
    lifecycle.extend_audio(bytes([0]*(16886)))

    # but timeout has not happened yet
    assert lifecycle.handle_command_finised.call_count == 0

    with freeze_time(lifecycle.timeout_manager.timeout_time):
        lifecycle.extend_audio(bytes([0]))

    # timeout has now happened
    assert lifecycle.handle_command_finised.call_count == 1


def test_e2e_no_wakeword(enable_snowboy):
    class AudioLifecycle(MockCallbackMixin, BaseAudioLifecycle):
        timeout_manager_class = timeout.ImmediateTimeoutManager

    lifecycle = AudioLifecycle()

    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0

    with wave.open('./tests/resources/jim_what_time_is_it.wav', 'rb') as f:
        for i in range(int(f.getnframes()/1024)):
            frame = f.readframes(1024)
            lifecycle.extend_audio(frame)

    assert lifecycle.handle_command_started.call_count == 0
    assert lifecycle.handle_command_finised.call_count == 0
