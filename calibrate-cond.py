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
    print("calibrating for dry sensor")
    input("press enter when ready")
    sensor.write("Z0")
    assert sensor.read().decode("utf8") == "dry cal"

    # place sensor in high side calibration solution.
    print("calibrating for high side: {}".format(cal.high_resp))
    input("press enter when ready")
    sensor.write("C")
    print("waiting 5 minutes for sensor to stabilize...", end="")
    time.sleep(5 * 60)
    sensor.write(cal.high_cmd)
    sensor.write("E")
    print("done")

    # place sensor in low side calibration solution.
    print("calibrating for low side: {}".format(cal.low_resp))
    input("press enter when ready")
    sensor.write("C")
    print("waiting 5 minutes for sensor to stabilize...", end="")
    time.sleep(5 * 60)
    sensor.write(cal.low_cmd)
    sensor.write("E")
    print("done")
finally:
    gpio.cleanup()
