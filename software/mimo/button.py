"""
Yamper button handler.

Reads the 16mm momentary push button via RPi.GPIO.
The button connects between BUTTON_PIN and GND (internal pull-up used).
An optional LED ring is driven from BUTTON_LED_PIN.
"""

import time

from . import config

# Try to import RPi.GPIO — falls back to a stub on non-Pi machines.
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False


class _GPIOStub:
    """Minimal stub so code can be tested on a laptop."""
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    FALLING = "FALLING"
    HIGH = 1
    LOW = 0

    @staticmethod
    def setmode(mode): pass
    @staticmethod
    def setup(pin, direction, pull_up_down=None): pass
    @staticmethod
    def input(pin): return 1  # not pressed (pull-up)
    @staticmethod
    def output(pin, value): pass
    @staticmethod
    def wait_for_edge(pin, edge, bouncetime=200, timeout=None): return pin
    @staticmethod
    def cleanup(): pass
    @staticmethod
    def setwarnings(flag): pass


if not GPIO_AVAILABLE:
    print("[button] RPi.GPIO not available — using stub")
    GPIO = _GPIOStub()


class ButtonHandler:
    """
    Push-to-talk button controller.

    Usage:
        btn = ButtonHandler()
        btn.wait_for_press()    # blocks until pressed
        while btn.is_pressed():
            ...                 # record while held
        btn.cleanup()
    """

    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.BUTTON_LED_PIN, GPIO.OUT)
        self.set_led(False)
        print(f"[button] ready on GPIO {config.BUTTON_PIN}")

    def wait_for_press(self, timeout=None):
        """
        Block until the button is pressed (falling edge).
        Returns True if pressed, False if timed out.
        timeout is in seconds (None = wait forever).
        """
        timeout_ms = int(timeout * 1000) if timeout else None
        result = GPIO.wait_for_edge(
            config.BUTTON_PIN, GPIO.FALLING,
            bouncetime=200, timeout=timeout_ms
        )
        return result is not None

    def is_pressed(self):
        """Return True if the button is currently held down."""
        return GPIO.input(config.BUTTON_PIN) == GPIO.LOW

    def set_led(self, on):
        """Turn the button LED ring on or off."""
        GPIO.output(config.BUTTON_LED_PIN, GPIO.HIGH if on else GPIO.LOW)

    def cleanup(self):
        """Release GPIO resources."""
        self.set_led(False)
        GPIO.cleanup()
        print("[button] GPIO cleaned up")
