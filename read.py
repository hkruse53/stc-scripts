#!/usr/bin/python3

import RPi.GPIO as gpio
import datetime
import time
import atsci

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

    # second sensor -- conductivity
    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.HIGH)
    # the conductivity sensor requires temperature in the format TT.T, i,e., with
    # 3 digits of precision
    sensor.write("{:.3},C".format(temp))

    # Take 20 readings for the sensor to become accurate.
    for i in range(20):
        sensor.read()

    cond = int(sensor.read().split(b",")[0])
    sensor.write("E")

    # third sensor -- pH
    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)
    # the pH sensor supports up to 4 digits of precision
    sensor.write("{:.4}".format(temp))
    sensor.write("R")
    ph = float(sensor.read())

    now = datetime.datetime.now()
    print("{}\t{}\t{}\t{}".format(now, temp, cond, ph))
finally:
    gpio.cleanup()
