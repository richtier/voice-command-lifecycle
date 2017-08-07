from unittest.mock import patch, PropertyMock

import pytest



@pytest.fixture(autouse=True)
def mock_snowboy():
    path = (
        'command_lifecycle.wakeword.SnowboyWakewordDetector.'
        'wakeword_library_import_path'
    )
    stub = patch(path, PropertyMock(return_value='unittest.mock.Mock'))
    stub.start()
    yield stub
    stub.stop()
