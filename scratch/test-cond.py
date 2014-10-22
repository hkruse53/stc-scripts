#!/usr/bin/python3

import RPi.GPIO as gpio
import time
import atsci

try:
    gpio.setmode(gpio.BOARD)

    gpio.setup(18, gpio.OUT)
    gpio.setup(16, gpio.OUT)

    sensor = atsci.AtSciSensor("/dev/ttyAMA0")

    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.HIGH)

    sensor.write("C,0")
    print(sensor.read())
finally:
    gpio.cleanup()
