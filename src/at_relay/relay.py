"""Relay board with serial connection controlled via AT commands."""
import time
from typing import Optional
import serial

from .error import CommunicationError, FailedCommandError


def configure_baudrate(device: str, baudrate: int, new_baudrate: int) -> bool:
    """Configure new baudrate for relay board.

    NOTE: The device will use the new baudrate _after_ a power cycle!

    Parameters
    ----------
    device : str
        path to serial device
    baudrate : int
        current baud rate
    new_baudrate : int
        new baudrate

    Returns
    -------
    bool
        True if baudrate change was successfull
    """
    _serial = serial.Serial(device, baudrate=baudrate, timeout=1)
    command = f"AT+BAUD={new_baudrate}"
    expected_respose = command.replace("AT", "OK")
    _serial.write((command + "\r\n").encode())

    response = _serial.readline().decode().strip()

    return response == expected_respose


class RelayBoard:
    """A AT command controlled relay board class."""

    def __init__(
        self,
        device: str,
        num_channels: int = None,
        baudrate: int = 9600,
        initial_state: bool = None,
    ) -> None:
        self._device = device
        self._num_channels = num_channels
        self._initial_state = initial_state
        self._baudrate = baudrate
        self._serial = None

        self._init_connection()

    def _init_connection(self):
        self._serial = serial.Serial(self._device, baudrate=self._baudrate, timeout=1)

        if not self.communication_ok():
            raise CommunicationError("Cannot communicate with usb relay")

        if self.num_channels is None:
            # try to get number of channels from relay board
            try:
                response = self._send_command("at+num=?")
                self._num_channels = int(response.split("=")[1])
            except FailedCommandError:
                # raise RuntimeWarning("Unable to determine number of channels from relay board. Using 1 as default.")
                self._num_channels = 1

        # check if number of channels matches relay by fetching status for each relay
        for channel in range(1, self.num_channels + 1):
            try:
                self.get_state(channel)
                if self._initial_state is not None:
                    self.set_state(channel, self._initial_state)
            except Exception as exc:
                raise ValueError(
                    "Invalid number of channels. "
                    f"Relay reports only {channel - 1} channels."
                ) from exc

    def __del__(self) -> None:
        """Close serial connection on class destruction."""
        if hasattr(self, "_serial") and self._serial is not None:
            self._serial.close()

    def communication_ok(self) -> bool:
        """Check if communication with relay board can be established.

        Returns
        -------
        bool
            True if communication can be established
        """
        response = self._send_command("AT", check=False)

        return response == "OK"

    def on(self, channel: int = 1) -> None:
        """Switch on a relay.

        Parameters
        ----------
        channel : int, optional
            relay channel, by default 1
        """
        self.set_state(channel, True)

    def off(self, channel: int = 1) -> None:
        """Switch off a relay.

        Parameters
        ----------
        channel : int, optional
            relay channel, by default 1
        """
        self.set_state(channel, False)

    def toggle(self, channel: int = 1) -> bool:
        """Toggle a relay.

        Parameters
        ----------
        channel : int, optional
            relay channel, by default 1
        """
        current_state = self.get_state(channel)
        new_state = not current_state

        self.set_state(channel, new_state)

        return new_state

    def get_state(self, channel: int) -> bool:
        """Get current state of a relay.

        Parameters
        ----------
        channel : int, optional
            relay channel
        """
        if channel <= 0 or channel > self._num_channels:
            raise ValueError("Invalid channel number")

        command = f"AT+CH{channel}=?"

        response = self._send_command(command)
        _, state = response.split("=")

        return state == "1"

    def set_state(self, channel: int, state: bool) -> None:
        """Switch off a relay.

        Parameters
        ----------
        channel : int
            relay channel
        state : bool
            new relay state
        """
        if channel <= 0 or channel > self._num_channels:
            raise ValueError("Invalid channel number")

        command = f"AT+CH{channel}={int(state)}"

        self._send_command(command)

    def _send_command(self, command: str, check: bool = True) -> str:
        """Send command to relay board.

        Parameters
        ----------
        command : str
            command to send
        check : bool, optional
            check response from relay board, by default True

        Returns
        -------
        str
            response from relay board

        Raises
        ------
        FailedCommandError
            indicates that the response was invalid / erroneous
        """
        try:
            if not self._serial.is_open:
                self._init_connection()

            self._serial.write((command.upper() + "\r\n").encode())
            response = self._serial.readline().decode().strip()
        except serial.serialutil.SerialException:
            # TODO: error handling if serial connection is gone
            response = ""

        if check and not response.startswith("OK+"):
            raise FailedCommandError(f"Response from relay: {response}")

        return response

    @property
    def num_channels(self) -> int:
        """Return number of relay channels on the board.

        Returns
        -------
        int
            number of relay channels
        """
        return self._num_channels

    @property
    def version(self) -> str:
        """Return firmware version of relay board.

        Returns
        -------
        str
            firmware string

        Raises
        ------
        FailedCommandError
            indicates that the response was invalid / erroneous
        """
        command = "AT+VER=?"
        response = self._send_command(command, check=False)

        if response == "":
            raise FailedCommandError("Failed to determine firmware version")

        return response
