import pytest
from mock_serial import MockSerial

from tests.utils import create_mock_board


@pytest.fixture(scope="function")
def mock_board() -> MockSerial:
    num_channels = 4
    mock_serial = create_mock_board(num_channels)

    yield mock_serial

    mock_serial.close()
