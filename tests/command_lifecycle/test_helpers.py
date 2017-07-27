from command_lifecycle import helpers


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
