#!/usr/bin/python3

import RPi.GPIO as gpio
import atsci
import sys
import time

STABILIZE_MINS = 2

def calibrate(cmd, ph):
    print("place sensor in the pH {} solution".format(ph))
    input("press enter when ready")

    print("entering continuous mode for {} minute(s)".format(STABILIZE_MINS))
    sensor.write("C,1")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > STABILIZE_MINS * 60:
            break

        print("{:3}s: {:5}pH".format(int(elapsed), float(sensor.read())))
        time.sleep(1)

    print("calibrating for pH {}... ".format(ph), end="")
    sensor.write("{},{}".format(cmd, ph))
    print("done")

    # exit continuous mode.
    sensor.write("C,0")

try:
    low = sys.argv[1]
    mid = sys.argv[2]
    high = sys.argv[3]
except IndexError:
    print("Usage: {} LOW-SOLUTION MID-SOLUTION HIGH-SOLUTION".format(
        sys.argv[0]))
    sys.exit(1)

with atsci.AtSciSensor() as sensor:
    print("letting temperature stabilize for {} minute(s)".format(
        STABILIZE_MINS))
    sensor.switch(atsci.TEMP)
    sensor.write("C")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > STABILIZE_MINS * 60:
            break;

        print("{:3}s: {}C".format(int(elapsed), float(sensor.read())))
        time.sleep(1)

    sensor.write("E")
    sensor.write("R")
    temp = float(sensor.read())

    # Leave continuous mode and clear calibration.
    sensor.switch(atsci.PH)
    sensor.write("C,0")
    sensor.write("Cal,clear")

    print("adjusting temperature to {}°C".format(temp))
    sensor.write("T,{:.3}".format(temp))

    calibrate("Cal,mid", mid)
    calibrate("Cal,low", low)
    calibrate("Cal,high", high)
