import pytest

from command_lifecycle import timeout


class SimpleTimeoutManager(timeout.BaseTimeoutManager):
    allowed_silent_frames = 10


@pytest.fixture
def manager():
    return SimpleTimeoutManager()


def test_missing_timeout_seconds_subclass():
    class TimeoutManager(timeout.BaseTimeoutManager):
        pass

    expected_message = (
        "Can't instantiate abstract class TimeoutManager with abstract "
        "methods timeout_seconds"
    )
    with pytest.raises(TypeError, message=expected_message):
        TimeoutManager()


def test_allowed_silent_frames():
    assert timeout.ShortTimeoutManager.allowed_silent_frames == 10
    assert timeout.MediumTimeoutManager.allowed_silent_frames == 15
    assert timeout.LongTimeoutManager.allowed_silent_frames == 20


def test_increment(manager):
    assert manager.elapsed_silent_frames == 0

    manager.increment()

    assert manager.elapsed_silent_frames == 1


def test_reset(manager):
    manager.elapsed_silent_frames = 10

    assert manager.elapsed_silent_frames == 10

    manager.reset()

    assert manager.elapsed_silent_frames == 0


@pytest.mark.parametrize('allowed,elapsed,expected', [
    [5, 0, False],
    [5, 4, False],
    [5, 5, True],
    [5, 6, True],
])
def test_has_timedout(manager, allowed, elapsed, expected):
    manager.allowed_silent_frames = allowed
    manager.elapsed_silent_frames = elapsed

    assert manager.has_timedout() is expected


@pytest.mark.parametrize('allowed,elapsed,expected', [
    [5, 0, 5],
    [5, 4, 1],
    [5, 5, 0],
    [5, 6, -1],
])
def test_remaining_silent_frames(manager, allowed, elapsed, expected):
    manager.allowed_silent_frames = allowed
    manager.elapsed_silent_frames = elapsed

    assert manager.remaining_silent_frames == expected
