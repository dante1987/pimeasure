import time

import RPi.GPIO as gpio

PIN_NUMBER = 13
BLINK_TIME = 1.5


def led_blink(pin_number=PIN_NUMBER, blink_time=BLINK_TIME):
    gpio.setmode(gpio.BOARD)
    gpio.setup(pin_number, gpio.OUT)

    gpio.output(pin_number, gpio.HIGH)
    time.sleep(blink_time)
    gpio.output(pin_number, gpio.LOW)

    gpio.cleanup()


if __name__ == '__main__':
    led_blink()
