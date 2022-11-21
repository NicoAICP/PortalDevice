"""Safe mode class for Pi Pico
"""
from typing import Optional

import microcontroller
from digitalio import DigitalInOut, Pull

def enable(pin: microcontroller.Pin, pull: Optional[Pull] = None):
    """Enables safe mode

    :param ~microcontroller.Pin pin: The pin to control
    :param Pull pull: pull configuration for the input
    """
    safe = DigitalInOut(pin)
    safe.switch_to_input(pull)
    if (pull is Pull.UP and safe.value is False) or (pull is Pull.DOWN and safe.value is True):
        microcontroller.on_next_reset(microcontroller.RunMode.SAFE_MODE)
        microcontroller.reset()