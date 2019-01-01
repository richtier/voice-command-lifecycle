import pytest

from command_lifecycle import wakeword
from command_lifecycle.buffer import WakewordAudioBuffer


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


def test_wakeword_get_uttered_wakeword_name():
    buffer = WakewordAudioBuffer([1, 2])
    snowboy_detector = wakeword.SnowboyWakewordDetector()

    snowboy_detector.detector.RunDetection.return_value = 1

    assert snowboy_detector.get_uttered_wakeword_name(buffer) is (
        snowboy_detector.ALEXA
    )


@pytest.mark.parametrize("code", [-2, -1, 0])
def test_wakeword_get_uttered_wakeword_name_precondition_unmet(code):
    buffer = WakewordAudioBuffer([1, 2])
    snowboy_detector = wakeword.SnowboyWakewordDetector()

    snowboy_detector.detector.RunDetection.return_value = code

    assert snowboy_detector.get_uttered_wakeword_name(buffer) is None
