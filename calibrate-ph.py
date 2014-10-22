#!/usr/bin/python3

import RPi.GPIO as gpio
import atsci
import sys
import time

WAIT_MINUTES = 2

def calibrate(cmd, ph):
    print("place sensor in the pH {} solution".format(ph))
    input("press enter when ready")

    print("entering continuous mode for {} minute(s)".format(WAIT_MINUTES))
    sensor.write("C,1")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > WAIT_MINUTES * 60:
            break

        print("{:3}s: {:5}pH".format(int(elapsed), float(sensor.read())))
        time.sleep(1)

    print("calibrating for pH {}... ".format(ph), end="")
    sensor.write("{},{}".format(cmd, ph))
    print("done")

    # exit continuous mode.
    sensor.write("C,0")

low = sys.argv[1]
mid = sys.argv[2]
high = sys.argv[3]

try:
    gpio.setmode(gpio.BOARD)

    gpio.setup(18, gpio.OUT)
    gpio.setup(16, gpio.OUT)

    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.LOW)

    sensor = atsci.AtSciSensor("/dev/ttyAMA0")

    # first sensor -- temperature
    sensor.write("R")
    temp = float(sensor.read())

    # third sensor -- pH
    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)

    # Leave continuous mode and clear calibration.
    sensor.write("C,0")
    sensor.write("Cal,clear")

    # Set up temperature compensation.
    print("adjusting temperature to {}°C".format(temp))
    sensor.write("T,{:.3}".format(temp))

    calibrate("Cal,mid", mid)
    calibrate("Cal,low", low)
    calibrate("Cal,high", high)
finally:
    gpio.cleanup()
