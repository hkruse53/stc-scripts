#!/usr/bin/python3

import time
import atsci
import RPi.GPIO as gpio

gpio.setmode(gpio.BOARD)

gpio.setup(18, gpio.OUT)
gpio.setup(16, gpio.OUT)

gpio.output(18, gpio.LOW)
gpio.output(16, gpio.LOW)

sensor = atsci.AtSciSensor("/dev/ttyAMA0")
sensor.write("E")

sensor.write("SF")
sensor.write("R")
print(float(sensor.read()))

sensor.write("SC")
sensor.write("R")

print(float(sensor.read()))
