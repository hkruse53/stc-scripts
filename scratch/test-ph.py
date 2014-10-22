#!/usr/bin/python3

import RPi.GPIO as gpio
import time
import atsci

try:
    gpio.setmode(gpio.BOARD)

    gpio.setup(18, gpio.OUT)
    gpio.setup(16, gpio.OUT)

    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)

    sensor = atsci.AtSciSensor("/dev/ttyAMA0")
    sensor.write("R")
    print(sensor.read())
finally:
    gpio.cleanup()
