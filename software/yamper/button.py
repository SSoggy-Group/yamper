import time
from . import config

try:
    import RPi.GPIO as GPIO
    has_gpio = True
except:
    has_gpio = False

# fake gpio for testing on mac
class FakeGPIO:
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    FALLING = "FALLING"
    HIGH = 1
    LOW = 0
    
    def setmode(self, mode): pass
    def setup(self, pin, direction, pull_up_down=None): pass
    def input(self, pin): return 1
    def output(self, pin, value): pass
    def wait_for_edge(self, pin, edge, bouncetime=200, timeout=None): return pin
    def cleanup(self): pass
    def setwarnings(self, flag): pass

if not has_gpio:
    print("no RPi.GPIO found, using fake gpio")
    GPIO = FakeGPIO()

class Button:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.BUTTON_LED_PIN, GPIO.OUT)
        self.set_led(False)

    def wait_for_press(self, timeout=None):
        timeout_ms = int(timeout * 1000) if timeout else None
        res = GPIO.wait_for_edge(
            config.BUTTON_PIN, 
            GPIO.FALLING,
            bouncetime=200, 
            timeout=timeout_ms
        )
        return res is not None

    def is_pressed(self):
        return GPIO.input(config.BUTTON_PIN) == GPIO.LOW

    def set_led(self, on):
        GPIO.output(config.BUTTON_LED_PIN, GPIO.HIGH if on else GPIO.LOW)

    def cleanup(self):
        self.set_led(False)
        GPIO.cleanup()
