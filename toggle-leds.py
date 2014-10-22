#!/usr/bin/python3

import RPi.GPIO as gpio
import time
import atsci

def toggle(sensor):
    sensor.write("L,?")

    if sensor.read()[3] == ord('1'):
        sensor.write("L,0")
    else:
        sensor.write("L,1")

    sensor.flush()

with atsci.AtSciSensor() as sensor:
    # second sensor -- conductivity
    gpio.output(18, gpio.LOW)
    gpio.output(16, gpio.HIGH)
    toggle(sensor)

    # third sensor -- pH
    gpio.output(18, gpio.HIGH)
    gpio.output(16, gpio.LOW)
    toggle(sensor)
