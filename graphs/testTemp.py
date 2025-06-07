
#
# calculate all graphs
#
# SwitchDoc Labs March 30, 2015

import TemperatureHumidityGraph
import sys
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BCM)


TemperatureHumidityGraph.TemperatureHumidityGraph('test', 10, 0)
