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
    sensor.switch(atsci.COND)
    toggle(sensor)

    sensor.switch(atsci.PH)
    toggle(sensor)
