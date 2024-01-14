from at_relay import configure_baudrate
from mock_serial import MockSerial

from tests.utils import _command


def test_configure_baudrate(mock_board: MockSerial) -> None:
    _command(mock_board, "AT+BAUD=115200", "OK+BAUD=115200", name="cmd_baudrate")

    assert configure_baudrate(mock_board.port, 9600, 115200)

    _command(mock_board, "AT+BAUD=115200", "OK+BAUD=9600", name="cmd_baudrate")

    assert not configure_baudrate(mock_board.port, 9600, 115200)

    del mock_board.stubs["cmd_baudrate"]

    assert not configure_baudrate(mock_board.port, 9600, 115200)
