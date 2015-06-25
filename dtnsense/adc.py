# Original credit to Stephen Hackman, 2015.

import RPi.GPIO as gpio

# SPI clock, input, and output gpio pins.
SPICLK = 23
SPIMISO = 21
SPIMOSI = 19
# Setting this high puts the adc into low-power mode.
STANDBY = 15
# Maximum reply from the 10-bit adc.
MAX_REPLY = 1024

# ADC channel for power supply voltage.
SUPPLY_CHANNEL = 0

class ADC:
    def __init__(self, channel, max_voltage):
        if channel > 7 or channel < 0:
            raise ValueError

        gpio.setup(SPIMOSI, gpio.OUT)
        gpio.setup(SPIMISO, gpio.IN)
        gpio.setup(SPICLK, gpio.OUT)
        gpio.setup(STANDBY, gpio.OUT)

        self.channel = channel
        self.divisor = MAX_REPLY / max_voltage

    def send_cmd(self):
        cmd = self.channel
        # start bit + single-ended bit
        cmd |= 0x18
        # we only need to send 5 bits here
        cmd <<= 3

        for i in range(5):
            gpio.output(SPIMOSI, cmd & 0x80 != 0)
            cmd <<= 1

            gpio.output(SPICLK, True)
            gpio.output(SPICLK, False)

    def read_reply(self):
        reply = 0

        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
            gpio.output(SPICLK, True)
            gpio.output(SPICLK, False)

            reply <<= 1

            if gpio.input(SPIMISO):
                reply |= 0x1

        # first bit is null so drop it
        reply >>= 1

        return reply

    # Convert 10bit reply into voltage up to max_voltage
    def to_voltage(self, reply):
        return reply / self.divisor

    def read(self):
        # start clock low
        gpio.output(SPICLK, False)
        gpio.output(STANDBY, False)

        self.send_cmd()
        reply = self.read_reply()

        gpio.output(STANDBY, True)

        return self.to_voltage(reply)
