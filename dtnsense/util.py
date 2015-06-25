import RPi.GPIO as gpio

class GPIOGuard:
    def __enter__(self):
        gpio.setmode(gpio.BOARD)

    def __exit__(self, *args):
        gpio.cleanup()
