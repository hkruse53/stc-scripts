#!/usr/bin/python3

import RPi.GPIO as gpio
import time
import atsci

try:
    gpio.setmode(gpio.BOARD)
    gpio.setup(16, gpio.OUT)

    sensor = atsci.AtSciSensor("/dev/ttyAMA0")

    gpio.output(16, gpio.LOW)
    sensor.write("L1")
    sensor.write("E")
    sensor.write("R")
    print(float(sensor.read()))
    time.sleep(2)
    sensor.write("L0")

    gpio.output(16, gpio.HIGH)
    time.sleep(2)
finally:
    gpio.cleanup()
