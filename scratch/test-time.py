#!/usr/bin/python3

import time
import datetime

t = time.time()
print(t)
d = datetime.date.fromtimestamp(t)
print(d)
dt = datetime.datetime.fromtimestamp(t)
print(dt)
