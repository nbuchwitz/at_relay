import pytest
from at_relay import RelayBoard
from at_relay.error import CommunicationError, FailedCommandError
from mock_serial import MockSerial

from tests.utils import _command


def test_init(mock_board: MockSerial) -> None:
    RelayBoard(mock_board.port)


def test_init_with_state(mock_board: MockSerial) -> None:
    _command(mock_board, "AT+CH1=?", "OK+CH1=1", name="cmd_ch1_?")
    RelayBoard(mock_board.port, initial_state=True)

def test_num_channels(mock_board: MockSerial):
    board = RelayBoard(mock_board.port)
    assert board.num_channels == 4

    # Emulate response from a device, which doesn't support the AT+NUM=? command
    _command(mock_board, "AT+NUM=?", "Error", name="test_num_channels")

    board = RelayBoard(mock_board.port)
    assert board.num_channels == 1

def test_broken_communication(mock_board: MockSerial) -> None:
    with pytest.raises(CommunicationError):
        # wrong response
        _command(mock_board, "AT", "FOO", name="test_command")
        RelayBoard(mock_board.port)

    with pytest.raises(CommunicationError):
        # no response
        del mock_board.stubs["test_command"]
        RelayBoard(mock_board.port)


def test_cmd_firmware(mock_board: MockSerial) -> None:
    version_string = "Dummy Firmware 1.0"

    _command(mock_board, "AT+VER=?", version_string)

    board = RelayBoard(mock_board.port)

    assert board.version.strip() == version_string


def test_cmd_firmware_failed(mock_board: MockSerial) -> None:
    with pytest.raises(FailedCommandError):
        _command(mock_board, "AT+VER=?", "")
        board = RelayBoard(mock_board.port)
        board.version()
