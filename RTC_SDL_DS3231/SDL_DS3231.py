#!/usr/bin/env python

# SDL_DS3231.py Python Driver Code
# SwitchDoc Labs 12/19/2014
# V 1.2
# only works in 24 hour mode
# now includes reading and writing the AT24C32 included on the SwitchDoc Labs
# DS3231 / AT24C32 Module (www.switchdoc.com)

#encoding: utf-8

# Copyright (C) 2013 @XiErCh

from datetime import datetime
import time
import smbus

def _bcd_to_int(bcd):
    """Decode a 2x4bit BCD to an integer."""
    out = 0
    for d in (bcd >> 4, bcd):
        for p in (1, 2, 4, 8):
            if d & 1:
                out += p
            d >>= 1
        out *= 10
    return out // 10

def _int_to_bcd(n):
    """Encode a one or two digit number to BCD."""
    bcd = 0
    for i in (n // 10, n % 10):
        for p in (8, 4, 2, 1):
            if i >= p:
                bcd += 1
                i -= p
            bcd <<= 1
    return bcd >> 1

class SDL_DS3231():
    _REG_SECONDS = 0x00
    _REG_MINUTES = 0x01
    _REG_HOURS = 0x02
    _REG_DAY = 0x03
    _REG_DATE = 0x04
    _REG_MONTH = 0x05
    _REG_YEAR = 0x06
    _REG_CONTROL = 0x07

    def __init__(self, twi=1, addr=0x68, at24c32_addr=0x57):
        self._bus = smbus.SMBus(twi)
        self._addr = addr
        self._at24c32_addr = at24c32_addr

    def _write(self, register, data):
        self._bus.write_byte_data(self._addr, register, data)

    def _read(self, data):
        return self._bus.read_byte_data(self._addr, data)

    def _read_seconds(self):
        return _bcd_to_int(self._read(self._REG_SECONDS) & 0x7F)

    def _read_minutes(self):
        return _bcd_to_int(self._read(self._REG_MINUTES))

    def _read_hours(self):
        d = self._read(self._REG_HOURS)
        if d == 0x64:
            d = 0x40
        return _bcd_to_int(d & 0x3F)

    def _read_day(self):
        return _bcd_to_int(self._read(self._REG_DAY))

    def _read_date(self):
        return _bcd_to_int(self._read(self._REG_DATE))

    def _read_month(self):
        return _bcd_to_int(self._read(self._REG_MONTH))

    def _read_year(self):
        return _bcd_to_int(self._read(self._REG_YEAR))

    def read_all(self):
        """Return a tuple: (year, month, date, day, hours, minutes, seconds)."""
        return (
            self._read_year(),
            self._read_month(),
            self._read_date(),
            self._read_day(),
            self._read_hours(),
            self._read_minutes(),
            self._read_seconds()
        )

    def read_str(self):
        """Return a string like 'YY-MM-DDTHH:MM:SS'."""
        return '%02d-%02d-%02dT%02d:%02d:%02d' % (
            self._read_year(),
            self._read_month(),
            self._read_date(),
            self._read_hours(),
            self._read_minutes(),
            self._read_seconds()
        )

    def read_datetime(self, century=21, tzinfo=None):
        """Return a datetime.datetime object."""
        return datetime(
            (century - 1) * 100 + self._read_year(),
            self._read_month(),
            self._read_date(),
            self._read_hours(),
            self._read_minutes(),
            self._read_seconds(),
            0,
            tzinfo=tzinfo
        )

    def write_all(self, seconds=None, minutes=None, hours=None, day=None,
                  date=None, month=None, year=None):
        """Write time values to DS3231."""
        if seconds is not None:
            if not (0 <= seconds <= 59):
                raise ValueError('Seconds out of range [0,59].')
            self._write(self._REG_SECONDS, _int_to_bcd(seconds))

        if minutes is not None:
            if not (0 <= minutes <= 59):
                raise ValueError('Minutes out of range [0,59].')
            self._write(self._REG_MINUTES, _int_to_bcd(minutes))

        if hours is not None:
            if not (0 <= hours <= 23):
                raise ValueError('Hours out of range [0,23].')
            self._write(self._REG_HOURS, _int_to_bcd(hours))

        if year is not None:
            if not (0 <= year <= 99):
                raise ValueError('Years out of range [0,99].')
            self._write(self._REG_YEAR, _int_to_bcd(year))

        if month is not None:
            if not (1 <= month <= 12):
                raise ValueError('Month out of range [1,12].')
            self._write(self._REG_MONTH, _int_to_bcd(month))

        if date is not None:
            if not (1 <= date <= 31):
                raise ValueError('Date out of range [1,31].')
            self._write(self._REG_DATE, _int_to_bcd(date))

        if day is not None:
            if not (1 <= day <= 7):
                raise ValueError('Day out of range [1,7].')
            self._write(self._REG_DAY, _int_to_bcd(day))

    def write_datetime(self, dt):
        """Write from a datetime.datetime object."""
        self.write_all(dt.second, dt.minute, dt.hour,
                       dt.isoweekday(), dt.day, dt.month, dt.year % 100)

    def write_now(self):
        """Write current system datetime."""
        self.write_datetime(datetime.now())

    def getTemp(self):
        byte_tmsb = self._bus.read_byte_data(self._addr, 0x11)
        byte_tlsb = bin(self._bus.read_byte_data(self._addr, 0x12))[2:].zfill(8)
        return byte_tmsb + int(byte_tlsb[0]) * 2**-1 + int(byte_tlsb[1]) * 2**-2

    # AT24C32 EEPROM Functions

    def set_current_AT24C32_address(self, address):
        a1 = address // 256
        a0 = address % 256
        self._bus.write_i2c_block_data(self._at24c32_addr, a1, [a0])

    def read_AT24C32_byte(self, address):
        self.set_current_AT24C32_address(address)
        return self._bus.read_byte(self._at24c32_addr)

    def write_AT24C32_byte(self, address, value):
        a1 = address // 256
        a0 = address % 256
        self._bus.write_i2c_block_data(self._at24c32_addr, a1, [a0, value])
        time.sleep(0.20)
