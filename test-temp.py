#!/usr/bin/python3

import time
import atsci

sensor = atsci.AtSciSensor("/dev/ttyAMA0")

sensor.write("SF")
sensor.write("R")
print(float(sensor.read()))

sensor.write("SC")
sensor.write("R")
print(float(sensor.read()))
