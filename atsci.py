import serial

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
