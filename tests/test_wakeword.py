import pytest

from command_lifecycle import wakeword
from command_lifecycle.buffer import WakewordAudioBuffer


@pytest.mark.parametrize("code,expected", [
    (-2, False),
    (-1, False),
    (0, False),
    (1, True)
])
def test_wakeword_was_wakeword_uttered(code, expected):
    buffer = WakewordAudioBuffer([1, 2])
    snowboy_detector = wakeword.SnowboyWakewordDetector()

    snowboy_detector.detector.RunDetection.return_value = code

    assert snowboy_detector.was_wakeword_uttered(buffer) is expected


@pytest.mark.parametrize(("code", "expected"), [
    (-2, False),
    (-1, False),
    (0, True),
    (1, False)
])
def test_wakeword_is_talking(code, expected):
    buffer = WakewordAudioBuffer([1, 2])
    snowboy_detector = wakeword.SnowboyWakewordDetector()

    snowboy_detector.detector.RunDetection.return_value = code

    assert snowboy_detector.is_talking(buffer) is expected
