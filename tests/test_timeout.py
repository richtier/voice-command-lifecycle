from datetime import datetime, timedelta

from freezegun import freeze_time
import pytest

from command_lifecycle import timeout


class SimpleTimeoutManager(timeout.BaseTimeoutManager):
    allowed_silent_seconds = 1


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


def test_allowed_silent_seconds():
    assert timeout.ShortTimeoutManager.allowed_silent_seconds == 1
    assert timeout.MediumTimeoutManager.allowed_silent_seconds == 2
    assert timeout.LongTimeoutManager.allowed_silent_seconds == 3


def test_reset(manager):
    silence_started_time = datetime.utcnow() - timedelta(seconds=1)
    manager.silence_started_time = silence_started_time

    assert manager.silence_started_time == silence_started_time

    expected = datetime(2012, 1, 14, 3, 21, 34)
    with freeze_time(expected):
        manager.reset()

    assert manager.silence_started_time == expected


@freeze_time(datetime(2012, 1, 14, 3, 21, 34))
@pytest.mark.parametrize('allowed,elapsed,expected', [
    [5, 0, False],
    [5, 4, False],
    [5, 5, True],
    [5, 6, True],
])
def test_has_timedout(manager, allowed, elapsed, expected):
    manager.allowed_silent_seconds = allowed
    manager.silence_started_time = (
        datetime.utcnow() - timedelta(seconds=elapsed)
    )
    assert manager.has_timedout() is expected


@freeze_time(datetime(2012, 1, 14, 3, 21, 34))
@pytest.mark.parametrize('allowed,elapsed,expected', [
    [5, 0, 5],
    [5, 4, 1],
    [5, 5, 0],
    [5, 6, -1],
])
def test_remaining_silent_seconds(manager, allowed, elapsed, expected):
    manager.allowed_silent_seconds = allowed
    manager.silence_started_time = (
        datetime.utcnow() - timedelta(seconds=elapsed)
    )

    assert manager.remaining_silent_seconds == expected
