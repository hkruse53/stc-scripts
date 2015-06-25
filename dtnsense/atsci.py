import RPi.GPIO as gpio
import serial

DEFAULT_TTY = "/dev/ttyAMA0"
A_PIN = 18
B_PIN = 16

TEMP = (1, 1)
COND = (0, 1)
PH = (1, 0)

class AtSciSensor(serial.Serial):
    def __init__(self, tty=DEFAULT_TTY):
        gpio.setup(A_PIN, gpio.OUT)
        gpio.setup(B_PIN, gpio.OUT)

        # Set the pins before opening the serial device, so the garbage 0xff
        # byte is sent deterministically.
        gpio.output(A_PIN, gpio.HIGH)
        gpio.output(B_PIN, gpio.HIGH)

        super().__init__(tty, 38400)

        # The Pi's UART board sends an 0xFF byte every time the tty is opened,
        # so send a carriage to flush any sensors that are listening for a
        # command.
        self.write("")

    def write(self, cmd):
        super().write("{}\r".format(cmd).encode("ascii"))
        super().flush()

    def _read_bytes(self):
        while True:
            byte = super().read()

            if byte == b"\r":
                return

            yield byte

    def read(self):
        return b"".join(self._read_bytes())

    def switch(self, sensor):
        gpio.output(A_PIN, sensor[0])
        gpio.output(B_PIN, sensor[1])

    def ask(self, msg):
        self.flushInput()
        self.write(msg)

        return self.read()
