#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4:sw=4:et

import time
from at_relay import RelayBoard, configure_baudrate


def counter_loop(device: str, num_channels: int = None, sleep: float = 0.5):
    relay = RelayBoard(device, num_channels=num_channels, initial_state=False)

    bits = relay.num_channels
    max_value = 2**bits - 1
    value = 0

    while True:
        for bit in range(0, bits):
            state = bool(value & 1 << bit)

            relay.set_state(bit + 1, state)

        value += 1

        if value > max_value:
            value = 0

        time.sleep(sleep)


def toggle_loop(device: str, num_channels: int = None, sleep: float = 0.5) -> None:
    relay = RelayBoard(device, num_channels=num_channels, initial_state=False)
    n = 0
    while True:
        for channel in range(1, relay.num_channels + 1):
            relay.toggle(channel)
            time.sleep(sleep)
        n += 1


if __name__ == "__main__":
    try:
        # configure_baudrate("/dev/ttyUSB0", 230400, 9600)
        # toggle_loop("/dev/ttyUSB0", 1)
        # toggle_loop("/dev/ttyACM0", 4, sleep=0.1)

        counter_loop("/dev/ttyACM0", sleep=0.25)
        # toggle_loop("/dev/ttyACM0", sleep=0.1)

        # relay = USBRelay("/dev/ttyACM0", num_channels=4, initial_state=False)
        # print(relay.version)
    except KeyboardInterrupt:
        exit()
