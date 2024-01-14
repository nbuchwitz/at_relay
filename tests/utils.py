from mock_serial import MockSerial


def _command(
    mock_serial: MockSerial, cmd: str, response: str, *, name: str = None
) -> None:
    mock_serial.stub(
        name=name,
        receive_bytes=f"{cmd}\r\n".encode(),
        send_bytes=f"{response}\r\n".encode(),
    )


def create_mock_board(num_channels: int = 1) -> MockSerial:
    mock_serial = MockSerial()

    _command(mock_serial, "AT", "OK", name="test_command")
    _command(mock_serial, "AT+NUM=?", f"OK+NUM={num_channels}", name="test_num_channels")

    for channel in range(1, num_channels + 1):
        for command, value in (("?", "0"), ("1", "1"), ("0", "0")):
            _command(
                mock_serial,
                f"AT+CH{channel}={command}",
                f"OK+CH{channel}={value}",
                name=f"cmd_ch{channel}_{command}",
            )

    mock_serial.open()

    return mock_serial
