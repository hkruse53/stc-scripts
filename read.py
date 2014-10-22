#!/usr/bin/python3

import RPi.GPIO as gpio
import atsci
import datetime
import time

# Wait 2 minutes for the temperature to stabilize.
TEMP_STABILIZE_SECS = 2 * 60

with atsci.AtSciSensor() as sensor:
    # first sensor -- temperature
    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.LOW)

    time.sleep(TEMP_STABILIZE_SECS)
    sensor.write("E")
    sensor.write("R")
    temp = float(sensor.read())

    # second sensor -- conductivity
    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.HIGH)
    # Set up temperature compensation.
    sensor.write("T,{:.3}".format(temp))

    sensor.write("R")
    [cond, tds, sal, sg] = (float(x) for x in sensor.read().split(b","))

    # third sensor -- pH
    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)
    # Set up temperature compensation.
    sensor.write("T,{:.3}".format(temp))
    sensor.write("R")
    ph = float(sensor.read())

    now = datetime.datetime.now()
    print("{}\t{}\t{}\t{}".format(now, temp, cond, ph))
