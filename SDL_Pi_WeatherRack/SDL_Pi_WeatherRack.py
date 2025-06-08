#
#
#
#  SDL_Pi_WeatherRack.py - Raspberry Pi Python Library for SwitchDoc Labs WeatherRack.
#
#  SparkFun Weather Station Meters
#  Argent Data Systems
#  Created by SwitchDoc Labs February 13, 2015
#  Released into the public domain.
#    Version 1.3 - remove 300ms Bounce
#    Version 2.0 - Update for WeatherPiArduino V2
#    Version 3.0 - Removed Double Interrupts
#

try:
    try:
        import conflocal as config
    except ImportError:
        import config
except:
    import NoWPAConfig.py as config

import sys
import time as time_

sys.path.append('./SDL_Adafruit_ADS1x15')

from SDL_Adafruit_ADS1x15 import ADS1x15
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
from datetime import *

SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1

SDL_MODE_SAMPLE = 0
SDL_MODE_DELAY = 1

SDL_INTERRUPT_CLICKS = 1
SDL_RAIN_BUCKET_CLICKS = 2

WIND_FACTOR = 2.400 / SDL_INTERRUPT_CLICKS


def fuzzyCompare(compareValue, value):
    VARYVALUE = 0.05
    if (value > (compareValue * (1.0 - VARYVALUE))) and (value < (compareValue * (1.0 + VARYVALUE))):
        return True
    return False


def voltageToDegrees(value, defaultWindDirection):
    ADJUST3OR5 = 1.0
    if fuzzyCompare(3.84 * ADJUST3OR5, value):
        return 0.0
    if fuzzyCompare(1.98 * ADJUST3OR5, value):
        return 22.5
    if fuzzyCompare(2.25 * ADJUST3OR5, value):
        return 45
    if fuzzyCompare(0.41 * ADJUST3OR5, value):
        return 67.5
    if fuzzyCompare(0.45 * ADJUST3OR5, value):
        return 90.0
    if fuzzyCompare(0.32 * ADJUST3OR5, value):
        return 112.5
    if fuzzyCompare(0.90 * ADJUST3OR5, value):
        return 135.0
    if fuzzyCompare(0.62 * ADJUST3OR5, value):
        return 157.5
    if fuzzyCompare(1.40 * ADJUST3OR5, value):
        return 180
    if fuzzyCompare(1.19 * ADJUST3OR5, value):
        return 202.5
    if fuzzyCompare(3.08 * ADJUST3OR5, value):
        return 225
    if fuzzyCompare(2.93 * ADJUST3OR5, value):
        return 247.5
    if fuzzyCompare(4.62 * ADJUST3OR5, value):
        return 270.0
    if fuzzyCompare(4.04 * ADJUST3OR5, value):
        return 292.5
    if fuzzyCompare(4.34 * ADJUST3OR5, value):
        return 315.0
    if fuzzyCompare(3.43 * ADJUST3OR5, value):
        return 337.5
    return defaultWindDirection


def micros():
    return int(round(time_.time() * 1000000))


class SDL_Pi_WeatherRack:

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    _currentWindCount = 0
    _currentRainCount = 0
    _shortestWindTime = 0
    _pinAnem = 0
    _pinRain = 0
    _intAnem = 0
    _intRain = 0
    _ADChannel = 0
    _ADMode = 0
    _currentWindSpeed = 0.0
    _currentWindDirection = 0.0
    _lastWindTime = 0
    _sampleTime = 5.0
    _selectedMode = SDL_MODE_SAMPLE
    _startSampleTime = 0
    _currentRainMin = 0
    _lastRainTime = 0

    def __init__(self, pinAnem, pinRain, intAnem, intRain, ADMode):
        GPIO.setup(pinAnem, GPIO.IN)
        GPIO.setup(pinRain, GPIO.IN)

        GPIO.add_event_detect(pinAnem, GPIO.RISING, callback=self.serviceInterruptAnem, bouncetime=40)
        GPIO.add_event_detect(pinRain, GPIO.RISING, callback=self.serviceInterruptRain, bouncetime=40)

        ADS1015 = 0x00
        self.gain = 6144
        self.sps = 250
        self.ads1015 = ADS1x15(ic=ADS1015, address=0x48)

        try:
            value = self.ads1015.readRaw(1, self.gain, self.sps)
            time_.sleep(1.0)
            value = self.ads1015.readRaw(1, self.gain, self.sps)
            if (0x0F & value) == 0:
                config.ADS1015_Present = True
                config.ADS1115_Present = False
                value = self.ads1015.readRaw(0, self.gain, self.sps)
                if (0x0F & value) == 0:
                    config.ADS1015_Present = True
                    config.ADS1115_Present = False
                else:
                    config.ADS1015_Present = False
                    config.ADS1115_Present = True
                    self.ads1015 = ADS1x15(ic=0x01, address=0x48)
            else:
                config.ADS1015_Present = False
                config.ADS1115_Present = True
                self.ads1015 = ADS1x15(ic=0x01, address=0x48)
        except TypeError as e:
            print("Type Error")
            config.ADS1015_Present = False
            config.ADS1115_Present = False

        SDL_Pi_WeatherRack._ADMode = ADMode

    def current_wind_direction(self):
        if SDL_Pi_WeatherRack._ADMode == SDL_MODE_I2C_ADS1015:
            value = self.ads1015.readADCSingleEnded(1, self.gain, self.sps)
            voltageValue = value / 1000
        else:
            voltageValue = 0.0
        direction = voltageToDegrees(voltageValue, SDL_Pi_WeatherRack._currentWindDirection)
        return direction

    def current_wind_direction_voltage(self):
        if SDL_Pi_WeatherRack._ADMode == SDL_MODE_I2C_ADS1015:
            value = self.ads1015.readADCSingleEnded(1, self.gain, self.sps)
            voltageValue = value / 1000
        else:
            voltageValue = 0.0
        return voltageValue

    def reset_rain_total(self):
        SDL_Pi_WeatherRack._currentRainCount = 0

    def accessInternalCurrentWindDirection(self):
        return SDL_Pi_WeatherRack._currentWindDirection

    def reset_wind_gust(self):
        SDL_Pi_WeatherRack._shortestWindTime = 0xffffffff

    def startWindSample(self, sampleTime):
        SDL_Pi_WeatherRack._startSampleTime = micros()
        SDL_Pi_WeatherRack._sampleTime = sampleTime

    def get_current_wind_speed_when_sampling(self):
        compareValue = SDL_Pi_WeatherRack._sampleTime * 1000000
        if (micros() - SDL_Pi_WeatherRack._startSampleTime) >= compareValue:
            timeSpan = micros() - SDL_Pi_WeatherRack._startSampleTime
            SDL_Pi_WeatherRack._currentWindSpeed = (
                float(SDL_Pi_WeatherRack._currentWindCount) / float(timeSpan)
            ) * WIND_FACTOR * 1000000.0
            SDL_Pi_WeatherRack._currentWindCount = 0
            SDL_Pi_WeatherRack._startSampleTime = micros()
        return SDL_Pi_WeatherRack._currentWindSpeed

    def setWindMode(self, selectedMode, sampleTime):
        SDL_Pi_WeatherRack._sampleTime = sampleTime
        SDL_Pi_WeatherRack._selectedMode = selectedMode
        if SDL_Pi_WeatherRack._selectedMode == SDL_MODE_SAMPLE:
            self.startWindSample(SDL_Pi_WeatherRack._sampleTime)

    def get_current_rain_total(self):
        rain_amount = 0.2794 * float(SDL_Pi_WeatherRack._currentRainCount) / SDL_RAIN_BUCKET_CLICKS
        SDL_Pi_WeatherRack._currentRainCount = 0
        return rain_amount

    def current_wind_speed(self):
        if SDL_Pi_WeatherRack._selectedMode == SDL_MODE_SAMPLE:
            SDL_Pi_WeatherRack._currentWindSpeed = self.get_current_wind_speed_when_sampling()
        else:
            SDL_Pi_WeatherRack._currentWindCount = 0
            time_.sleep(SDL_Pi_WeatherRack._sampleTime)
            SDL_Pi_WeatherRack._currentWindSpeed = (
                float(SDL_Pi_WeatherRack._currentWindCount)
                / float(SDL_Pi_WeatherRack._sampleTime)
            ) * WIND_FACTOR
        return SDL_Pi_WeatherRack._currentWindSpeed

    def get_wind_gust(self):
        latestTime = SDL_Pi_WeatherRack._shortestWindTime
        SDL_Pi_WeatherRack._shortestWindTime = 0xffffffff
        time_sec = latestTime / 1000000.0
        if time_sec == 0:
            return 0
        else:
            return (1.0 / float(time_sec)) * WIND_FACTOR

    def serviceInterruptAnem(self, channel):
        currentTime = micros() - SDL_Pi_WeatherRack._lastWindTime
        SDL_Pi_WeatherRack._lastWindTime = micros()
        if currentTime > 4000:
            SDL_Pi_WeatherRack._currentWindCount += 1
            if currentTime < SDL_Pi_WeatherRack._shortestWindTime:
                SDL_Pi_WeatherRack._shortestWindTime = currentTime
        else:
            print(f"currentTime={currentTime}")
            print(f"DEBOUNCE-count={SDL_Pi_WeatherRack._currentWindCount}")

    def serviceInterruptRain(self, channel):
        print("Rain Interrupt Service Routine")
        currentTime = micros() - SDL_Pi_WeatherRack._lastRainTime
        SDL_Pi_WeatherRack._lastRainTime = micros()
        if currentTime > 500:
            SDL_Pi_WeatherRack._currentRainCount += 1
            if currentTime < SDL_Pi_WeatherRack._currentRainMin:
                SDL_Pi_WeatherRack._currentRainMin = currentTime

    def returnInterruptClicks(self):
        return SDL_INTERRUPT_CLICKS
