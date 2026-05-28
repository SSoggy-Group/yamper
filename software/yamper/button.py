import time
from . import config

try:
    import RPi.GPIO as GPIO  # type: ignore
    has_gpio = True
except Exception:
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
    
    def setmode(self, mode): pass  # empty
    def setup(self, pin, direction, pull_up_down=None): pass  # empty
    def input(self, _pin):
        from . import eyes
        return self.LOW if eyes.fake_button_held else self.HIGH
    
    def output(self, _pin, value):
        if _pin == config.BUTTON_LED_PIN:
            state = "🟢 ON" if value == self.HIGH else "⚫ OFF"
            print(f"\n[Hardware] Button LED is now: {state}\n")

    def wait_for_edge(self, pin, edge, bouncetime=200, timeout=None):
        _ = edge; _ = bouncetime
        from . import eyes
        start = time.time()
        while not eyes.fake_button_held:
            if timeout and (time.time() - start) * 1000 > timeout:
                return None
            time.sleep(0.05)
        return pin
    def cleanup(self): pass  # empty
    def setwarnings(self, flag): pass  # empty

if not has_gpio:
    print("no RPi.GPIO found, using fake gpio")
    GPIO = FakeGPIO()

class Button:
    def __init__(self):
        GPIO.setwarnings(False)  # type: ignore
        GPIO.setmode(GPIO.BCM)  # type: ignore
        GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # type: ignore
        GPIO.setup(config.BUTTON_LED_PIN, GPIO.OUT)  # type: ignore
        self.set_led(False)

    def wait_for_press(self, timeout=None):
        timeout_ms = int(timeout * 1000) if timeout else None
        res = GPIO.wait_for_edge(config.BUTTON_PIN, GPIO.FALLING, bouncetime=200, timeout=timeout_ms)  # type: ignore
        return res is not None

    def is_pressed(self):
        return GPIO.input(config.BUTTON_PIN) == GPIO.LOW

    def set_led(self, on):
        GPIO.output(config.BUTTON_LED_PIN, GPIO.HIGH if on else GPIO.LOW)  # type: ignore

    def cleanup(self):
        self.set_led(False)
        GPIO.cleanup()
