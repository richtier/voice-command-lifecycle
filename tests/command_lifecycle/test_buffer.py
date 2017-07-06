import pytest

from command_lifecycle.buffer import CommandAudioBuffer, WakewordAudioBuffer


def test_maxlen_set():
    assert WakewordAudioBuffer().maxlen == 80000


def test_maxlen_unset():
    assert CommandAudioBuffer().maxlen is None


@pytest.mark.parametrize("Buffer", [WakewordAudioBuffer, CommandAudioBuffer])
def test_get_contents(Buffer):
    buffer = Buffer([1, 2, 3])

    assert buffer.get() == b'\x01\x02\x03'


@pytest.mark.parametrize("Buffer", [WakewordAudioBuffer, CommandAudioBuffer])
def test_popleft_size(Buffer):
    buffer = Buffer([1, 2, 3])

    assert buffer.popleft_size(2) == b'\x01\x02'
    assert buffer.get() == b'\x03'
