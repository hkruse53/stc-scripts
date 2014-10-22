import RPi.GPIO as gpio
import serial

DEFAULT_TTY = "/dev/ttyAMA0"

class AtSciSerial(serial.Serial):
    def __init__(self, tty):
        super().__init__(tty, 38400)

        # The Pi's UART board sends an 0xFF byte every time the tty is opened,
        # so send a carriage to flush any sensors that are listening for a
        # command.
        self.write("")
        self.flush()

    def write(self, cmd):
        super().write("{}\r".format(cmd).encode("ascii"))

    def _read_bytes(self):
        while True:
            byte = super().read()

            if byte == b"\r":
                return

            yield byte

    def read(self):
        return b"".join(self._read_bytes())

class AtSciSensor:
    __slots__ = ["tty"]

    def __init__(self, tty=DEFAULT_TTY):
        self.tty = tty

    def __enter__(self):
        gpio.setmode(gpio.BOARD)
        gpio.setup(18, gpio.OUT)
        gpio.setup(16, gpio.OUT)

        # Set the pins before opening the serial device, so the garbage 0xff
        # byte is sent deterministically.
        gpio.output(18, gpio.HIGH)
        gpio.output(16, gpio.HIGH)

        return AtSciSerial(self.tty)

    def __exit__(self, *args):
        gpio.cleanup()
