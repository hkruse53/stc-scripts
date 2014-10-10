#!/usr/bin/python3

import RPi.GPIO as gpio
import datetime
import time
import atsci

def calibrate(cond, cmd):
    print("place sensor in {} solution".format(cond))
    input("press enter when ready")

    print("entering continuous mode for 5 minutes")
    sensor.write("C")

    start = time.time()

    while True:
        elapsed = time.time() - start

        if elapsed > 5 * 60:
            break

        print("{:4}s: {}".format(int(elapsed), sensor.read().decode("ascii")))
        time.sleep(1)

    print("calibrating for {}...".format(cond), end="")
    sensor.write(cmd)
    print("done")

    sensor.write("E")

class CalibrationSet:
    __slots__ = ("sensor_cmd", "sensor_resp", "high_cmd", "high_resp",
                 "low_cmd", "low_resp")

    def __init__(self, sensor_cmd, sensor_resp, high_cmd, high_resp, low_cmd,
                 low_resp):
        self.sensor_cmd = sensor_cmd
        self.sensor_resp = sensor_resp
        self.high_cmd = high_cmd
        self.high_resp = high_resp
        self.low_cmd = low_cmd
        self.low_resp = low_resp

cals = {
    "K0.1": CalibrationSet("P,1", "k0.1",
                           "Z30", "3,000 μs/cm cal",
                           "Z2", "220 μs/cm cal"),
    "K1.0": CalibrationSet("P,2", "k1.0",
                           "Z40", "40,000 μs/cm cal",
                           "Z10", "10,500 μs/cm cal"),
    "K10.0": CalibrationSet("P,3", "k10",
                            "Z90", "90,000 μs/cm cal",
                            "Z62", "62,000 μs/cm cal")
}

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

    sensor.write("E")
    # the conductivity sensor requires temperature in the format TT.T, i,e., with
    # 3 digits of precision
    sensor.write("{:.3}".format(temp))
    print("adjusting temperature to {}°C".format(temp))
    # throw away response.
    sensor.read()

    probe = "K10.0"
    cal = cals[probe]
    print("using probe {}".format(probe))

    sensor.write(cal.sensor_cmd)
    assert sensor.read().decode("utf8") == cal.sensor_resp

    # calibrate for dry sensor.
    print("make sure the sensor is dry")
    input("press enter when ready")
    sensor.write("Z0")
    assert sensor.read().decode("utf8") == "dry cal"

    calibrate(cal.high_resp, cal.high_cmd)
    calibrate(cal.low_resp, cal.low_cmd)
finally:
    gpio.cleanup()
