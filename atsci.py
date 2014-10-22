import serial

class AtSciSerial(serial.Serial):
    def __init__(self, file):
        super().__init__(file, 38400)
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
