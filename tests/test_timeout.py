from unittest import mock

import pytest

from command_lifecycle import timeout


class SimpleTimeoutManager(timeout.BaseTimeoutManager):
    allowed_silent_seconds = 1


@pytest.fixture
def timeout_callback():
    return mock.Mock()


@pytest.fixture
def manager(timeout_callback):
    return SimpleTimeoutManager(timeout_callback)


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
