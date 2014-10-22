#!/usr/bin/python3

import RPi.GPIO as gpio
import atsci
import datetime
import time

# Wait 2 minutes for the temperature to stabilize.
TEMP_STABILIZE_SECS = 2 * 60

with atsci.AtSciSensor() as sensor:
    time.sleep(TEMP_STABILIZE_SECS)

    sensor.switch(atsci.TEMP)
    sensor.write("E")
    sensor.write("R")
    temp = float(sensor.read())

    sensor.switch(atsci.COND)
    sensor.write("T,{:.3}".format(temp))
    sensor.write("R")
    [cond, tds, sal, sg] = (float(x) for x in sensor.read().split(b","))

    sensor.switch(atsci.PH)
    sensor.write("T,{:.3}".format(temp))
    sensor.write("R")
    ph = float(sensor.read())

    now = datetime.datetime.now()
    print("{}\t{}\t{}\t{}".format(now, temp, cond, ph))
