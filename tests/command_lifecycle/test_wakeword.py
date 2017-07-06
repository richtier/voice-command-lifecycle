from unittest.mock import patch

import pytest

from command_lifecycle import wakeword
from command_lifecycle.buffer import WakewordAudioBuffer
from command_lifecycle.snowboy.snowboydetect import SnowboyDetect


@pytest.mark.parametrize("code,expected", [
    (-2, False),
    (-1, False),
    (0, False),
    (1, True)
])
def test_wakeword_was_wakeword_uttered(code, expected):
    buffer = WakewordAudioBuffer([1, 2])
    with patch.object(SnowboyDetect, 'RunDetection', return_value=code):
        detector = wakeword.WakewordDetector()
        assert detector.was_wakeword_uttered(buffer) is expected


@pytest.mark.parametrize(("code", "expected"), [
    (-2, False),
    (-1, False),
    (0, True),
    (1, False)
])
def test_wakeword_is_talking(code, expected):
    buffer = WakewordAudioBuffer([1, 2])
    with patch.object(SnowboyDetect, 'RunDetection', return_value=code):
        detector = wakeword.WakewordDetector()
        assert detector.is_talking(buffer) is expected
