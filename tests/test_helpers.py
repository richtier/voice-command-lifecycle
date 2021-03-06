from unittest.mock import Mock

from command_lifecycle import helpers, lifecycle


def test_webaudio_to_wav_audio_converters():
    input_value = [0.1111, 0.3322, 0.3323]
    output_value = helpers.WebAudioToWavConverter.convert(input_value)
    expected = b'8\x0e'
    assert output_value == expected


def test_webaudio_to_wav_handles_out_of_bounds_samples():
    input_value = [1.1, -0.32323, 0.1111, 0.3322, 0.3323, 1.1]
    output_value = helpers.WebAudioToWavConverter.convert(input_value)
    expected = b'\xa1\xd6\x87*'

    assert output_value == expected


def test_no_operation_converter():
    input_value = [0.1111, 0.3322, 0.3323]
    output_value = helpers.NoOperationConverter.convert(input_value)

    assert output_value == input_value


def test_lifecycle_filelike_reads_from_buffer():
    class AudioLifecycle(lifecycle.BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)

    audio_lifecycle = AudioLifecycle()
    audio_lifecycle.extend_audio(b'12345678')

    file_like = helpers.LifeCycleFileLike(audio_lifecycle)

    assert file_like.read(4) == b'1234'
    assert file_like.read(4) == b'5678'


def test_lifecycle_filelike_length_not_expecting_audio():
    class AudioLifecycle(lifecycle.BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)

    audio_lifecycle = AudioLifecycle()
    audio_lifecycle.extend_audio(b'12345678')
    audio_lifecycle.is_command_pending = False

    file_like = helpers.LifeCycleFileLike(audio_lifecycle)

    assert len(file_like) == 8


def test_lifecycle_filelike_length_expecting_audio():
    class AudioLifecycle(lifecycle.BaseAudioLifecycle):
        get_uttered_wakeword_name = Mock(return_value=None)

    audio_lifecycle = AudioLifecycle()
    audio_lifecycle.extend_audio(b'12345678')
    audio_lifecycle.is_command_pending = True

    file_like = helpers.LifeCycleFileLike(audio_lifecycle)

    assert len(file_like) == 1025


def test_wav_integer_samples_to_wav():
    input_value = [1, 2, 3, 4, 5]
    output_value = helpers.WavIntSamplestoWavConverter.convert(input_value)

    assert output_value == b'\x01\x00\x02\x00\x03\x00\x04\x00\x05\x00'
