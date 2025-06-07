#
# calculate all graphs
#
# SwitchDoc Labs March 30, 2015

import BarometerLightningGraph
import PowerVoltageGraph
import PowerCurrentGraph
import TemperatureHumidityGraph
import sys
sys.path.append('/home/pi/SDL_Pi_GroveWeatherPi/graphs')

# Check for user imports
try:
    import conflocal as config
except ImportError:
    import config


def doAllGraphs():

    if (config.enable_MySQL_Logging == True):

        BarometerLightningGraph.BarometerLightningGraph('test', 10, 0)
        TemperatureHumidityGraph.TemperatureHumidityGraph('test', 10, 0)
        PowerCurrentGraph.PowerCurrentGraph('test', 10, 0)
        PowerVoltageGraph.PowerVoltageGraph('test', 10, 0)
