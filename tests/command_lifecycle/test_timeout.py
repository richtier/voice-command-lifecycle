from datetime import datetime

from freezegun import freeze_time
import pytest

from command_lifecycle import timeout


class SimpleTimeoutManager(timeout.BaseTimeoutManager):
    timeout_seconds = 1


def test_missing_timeout_seconds_subclass():
    class TimeoutManager(timeout.BaseTimeoutManager):
        pass

    expected_message = (
        "Can't instantiate abstract class TimeoutManager with abstract "
        "methods timeout_seconds"
    )
    with pytest.raises(TypeError, message=expected_message):
        TimeoutManager()


def test_timeout_manager_seconds():
    assert timeout.ImmediateTimeoutManager.timeout_seconds == 0
    assert timeout.ShortTimeoutManager.timeout_seconds == 1
    assert timeout.MediumTimeoutManager.timeout_seconds == 2
    assert timeout.LongTimeoutManager.timeout_seconds == 4


@freeze_time(datetime(2012, 1, 14, 12, 0, 0))
def test_start_saves_timeout_time():
    timeout_manager = SimpleTimeoutManager()

    timeout_manager.start()

    # one second ahead of time
    assert timeout_manager.timeout_time == datetime(2012, 1, 14, 12, 0, 1)


def test_stop_ends_timeout_time():
    timeout_manager = SimpleTimeoutManager()

    timeout_manager.start()
    assert timeout_manager.timeout_time is not None

    timeout_manager.stop()
    assert timeout_manager.timeout_time is None


@pytest.mark.parametrize("current_time,expected", [
    [datetime(2012, 1, 14, 12, 0, 0), False],
    [datetime(2012, 1, 14, 12, 0, 1), True],
    [datetime(2012, 1, 14, 12, 0, 2), True],
])
def test_end_to_end(current_time, expected):
    timeout_manager = SimpleTimeoutManager()
    with freeze_time(datetime(2012, 1, 14, 12, 0, 0)):
        timeout_manager.start()
    with freeze_time(current_time):
        assert timeout_manager.has_timedout() is expected
