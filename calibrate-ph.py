#!/usr/bin/python3

import RPi.GPIO as gpio
import datetime
import time
import atsci

def calibrate(ph, cmd):
    print("place sensor in the pH {} solution".format(ph))
    input("press enter when ready")

    print("adjusting temperature to {}°C".format(temp))
    # the pH sensor supports up to 4 digits of precision
    sensor.write("{:.4}".format(temp))

    print("entering continuous mode for 2 minutes")
    sensor.write("C")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > 2 * 60:
            break

        print("{:3}s: {:5}pH".format(int(elapsed), float(sensor.read())))
        time.sleep(1)

    print("calibrating for pH {}... ".format(ph), end="")
    sensor.write(cmd)
    print("done")

    # exit continuous mode.
    sensor.write("E")

try:
    gpio.setmode(gpio.BOARD)

    gpio.setup(18, gpio.OUT)
    gpio.setup(16, gpio.OUT)

    sensor = atsci.AtSciSensor("/dev/ttyAMA0")

    # first sensor -- temperature
    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.LOW)
    sensor.write("R")
    temp = float(sensor.read())

    # third sensor -- pH
    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)

    calibrate(7, "S")
    calibrate(4, "F")
    calibrate(10, "T")
finally:
    gpio.cleanup()
