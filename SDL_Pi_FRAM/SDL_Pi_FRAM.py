#!/usr/bin/env python

# SDL_Pi_FRAM.py Python Driver Code
# SwitchDoc Labs 02/16/2014
# V 1.2

import time
import smbus

class SDL_Pi_FRAM:
    def __init__(self, twi=1, addr=0x50):
        self._bus = smbus.SMBus(twi)
        self._addr = addr

    def write8(self, address, data):
        self._bus.write_i2c_block_data(self._addr, address >> 8, [address % 256, data])

    def read8(self, address):
        self._bus.write_i2c_block_data(self._addr, address >> 8, [address % 256])
        returndata = self._bus.read_byte(self._addr)
        return returndata
