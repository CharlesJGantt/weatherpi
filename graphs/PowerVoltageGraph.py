# PowerVoltageGraph  
# filename: PowerVoltageGraph.py
# Version 1.3 09/12/13
# Version 1.4 03/30/15

import sys
import time
import RPi.GPIO as GPIO
import gc
import datetime

import matplotlib
matplotlib.use('Agg')  # Force matplotlib to not use any Xwindows backend

from matplotlib import pyplot
from matplotlib import dates
import pylab
import MySQLdb as mdb

# Check for user imports
try:
    import conflocal as config
except ImportError:
    import config

def PowerVoltageGraph(source, days, delay):
    print(f"PowerVoltageGraph source: {source} days: {days} delay: {delay}")
    print(f"sleeping: {delay}")
    time.sleep(delay)
    print("PowerVoltageGraph running now")

    # blink GPIO LED when it's run
    GPIO.setup(18, GPIO.OUT)
    GPIO.output(18, True)
    time.sleep(0.2)
    GPIO.output(18, False)

    # now we get the data, stuff it in the graph
    try:
        print("trying database")
        db = mdb.connect('localhost', 'root', config.MySQL_Password, 'GroveWeatherPi')
        cursor = db.cursor()

        query = (
            "SELECT TimeStamp, solarVoltage, batteryVoltage, loadVoltage "
            "FROM PowerSystem "
            "WHERE now() - interval %i hour < TimeStamp" % (days * 24)
        )
        cursor.execute(query)
        result = cursor.fetchall()

        t = []
        s = []
        u = []
        v = []

        for record in result:
            t.append(record[0])
            s.append(record[1])
            u.append(record[2])
            v.append(record[3])

        fig = pyplot.figure()
        print(f"count of t= {len(t)}")

        if len(t) == 0:
            return

        hfmt = dates.DateFormatter('%m/%d-%H')

        fig = pyplot.figure()
        fig.set_facecolor('white')
        ax = fig.add_subplot(111, facecolor='white')
        ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
        ax.xaxis.set_major_formatter(hfmt)
        ax.set_ylim(bottom=-200.0)
        pyplot.xticks(rotation='vertical')
        pyplot.subplots_adjust(bottom=.3)

        pylab.plot(t, s, color='b', label="Solar", linestyle="-", marker=".")
        pylab.plot(t, u, color='r', label="Battery", linestyle="-", marker=".")
        pylab.plot(t, v, color='g', label="Load", linestyle="-", marker=".")
        pylab.xlabel("Hours")
        pylab.ylabel("Voltage V")
        pylab.legend(loc='upper left')

        if max(u) > max(s):
            myMax = max(u) + 100.0
        else:
            myMax = max(s)
        pylab.axis([min(t), max(t), min(u), myMax])
        pylab.figtext(.5, .05, f"GroveWeatherPi Power Voltage Last {days} Days", fontsize=18, ha='center')
        pyplot.setp(ax.xaxis.get_majorticklabels(), rotation=70)
        pylab.grid(True)
        pyplot.show()

        try:
            pyplot.savefig("/home/pi/RasPiConnectServer/static/PowerVoltageGraph.png", facecolor=fig.get_facecolor())
        except:
            pyplot.savefig("/home/pi/SDL_Pi_GroveWeatherPi/static/PowerVoltageGraph.png", facecolor=fig.get_facecolor())

    except mdb.Error as e:
        print(f"Error {e.args[0]}: {e.args[1]}")
    finally:
        cursor.close()
        db.close()

        del cursor
        del db

        fig.clf()
        pyplot.close()
        pylab.close()
        del t, s, u, v
        gc.collect()
        print("PowerVoltageGraph finished now")
