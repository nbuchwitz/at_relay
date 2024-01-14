import pytest
from at_relay import RelayBoard
from mock_serial import MockSerial

from tests.utils import _command, create_mock_board


def test_switch_on_default(mock_board: MockSerial) -> None:
    board = RelayBoard(mock_board.port)
    board.on()


@pytest.mark.parametrize("num_channels", (1, 2, 4, 10))
def test_switch_on(num_channels: int) -> None:
    mock_board = create_mock_board(num_channels)
    board = RelayBoard(mock_board.port, num_channels=num_channels)

    for channel in range(1, num_channels + 1):
        board.on(channel)
        board.set_state(channel, True)


def test_switch_off_default(mock_board: MockSerial) -> None:
    board = RelayBoard(mock_board.port)
    board.off()


@pytest.mark.parametrize("num_channels", (1, 2, 4, 10))
def test_switch_off(num_channels: int) -> None:
    mock_board = create_mock_board(num_channels)
    board = RelayBoard(mock_board.port, num_channels=num_channels)

    for channel in range(1, num_channels + 1):
        board.off(channel)
        board.set_state(channel, False)


def test_toggle(mock_board: MockSerial) -> None:
    board = RelayBoard(mock_board.port)
    board.toggle()


def test_invalid_num_channels(mock_board: MockSerial) -> None:
    _command(mock_board, "AT+CH2=?", "Error")

    with pytest.raises(ValueError) as exc:
        RelayBoard(mock_board.port, 2)

        assert (
            str(exc)
            == "ValueError: Invalid number of channels. Relay reports only 1 channels."
        )


def test_invalid_channel(mock_board: MockSerial) -> None:
    with pytest.raises(ValueError):
        board = RelayBoard(mock_board.port, 1)
        board.get_state(2)

    with pytest.raises(ValueError):
        board = RelayBoard(mock_board.port, 1)
        board.set_state(2, True)
