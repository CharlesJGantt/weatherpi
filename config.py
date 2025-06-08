#
#
# configuration file - contains customization for exact system
# JCS 11/8/2013
#

# it is a good idea to copy this file into a file called "conflocal.py" and edit that instead of this one.  This file is wiped out if you update GroveWeatherPi.

# Email Settings
mailUser = "yourusename"
mailPassword = "yourmailpassword"
notifyAddress = "you@example.com"
fromAddress = "yourfromaddress@example.com"
textnotifyAddress = "yourphonenumber@yourprovider"

# MySQL/MariaDB Logging and Password Information
enable_MySQL_Logging = True
MySQL_Password = "wesave13.."
MySQL_User = 'weatheruser'
MySQL_Database_Name = "GroveWeatherPi"

# WLAN (WiFi) Settings
enable_WLAN_Detection = False
PingableRouterAddress = "192.168.0.27"

# WeatherUnderground Station Settings
WeatherUnderground_Present = False
WeatherUnderground_StationID = "KWXXXXX"
WeatherUnderground_StationKey = "YYYYYYY"

############
# Blynk configuration
############
USEBLYNK = False
BLYNK_AUTH = 'xxxxx'
BLYNK_URL = 'http://blynk-cloud.com/'

# Barometric Pressure Altitude
BMP280_Altitude_Meters = 62.0

# Device Present Flags
Lightning_Mode = True
SolarPower_Mode = False

TCA9545_I2CMux_Present = True
SunAirPlus_Present = False
AS3935_Present = False
DS3231_Present = True
BMP280_Present = True
FRAM_Present = False
HTU21DF_Present = False
HDC1080_Present = True
AM2315_Present = True
ADS1015_Present = False
ADS1115_Present = True
OLED_Present = True
OLED_Originally_Present = False
WXLink_Present = False
Sunlight_Preset = False

# Sunlight Gain (High Gain indoors = 1, Low Gain outdoors = 0)
Sunlight_Gain = 0

# WXLink Settings
WXLink_Data_Fresh = False
WXLInk_LastMessageID = 0
