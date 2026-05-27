"""
Yamper button handler module.

Manages GPIO interactions for the primary push-to-talk momentary switch
and its integrated LED indicator. Utilizes RPi.GPIO edge detection for
efficient state monitoring.
"""

import logging
from typing import Any, Optional

from . import config

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False


class _GPIOStub:
    """Minimal hardware stub to facilitate local testing and development."""
    BCM = "BCM"
    IN = "IN"
    OUT = "OUT"
    PUD_UP = "PUD_UP"
    FALLING = "FALLING"
    HIGH = 1
    LOW = 0

    @staticmethod
    def setmode(mode: str) -> None:
        pass

    @staticmethod
    def setup(pin: int, direction: str, pull_up_down: Optional[str] = None) -> None:
        pass

    @staticmethod
    def input(pin: int) -> int:
        return 1  # Simulates pull-up resistor state (not pressed)

    @staticmethod
    def output(pin: int, value: int) -> None:
        pass

    @staticmethod
    def wait_for_edge(pin: int, edge: str, bouncetime: int = 200, timeout: Optional[int] = None) -> Optional[int]:
        return pin

    @staticmethod
    def cleanup() -> None:
        pass

    @staticmethod
    def setwarnings(flag: bool) -> None:
        pass


if not GPIO_AVAILABLE:
    logger.debug("RPi.GPIO not found in environment. Initializing hardware stub.")
    GPIO = _GPIOStub()  # type: ignore


class ButtonHandler:
    """
    Controller for the push-to-talk button and LED.
    
    Abstracts raw GPIO operations into state querying and edge waiting methods.
    """

    def __init__(self) -> None:
        """Initialize GPIO pins based on configuration."""
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(config.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(config.BUTTON_LED_PIN, GPIO.OUT)
        
        self.set_led(False)
        logger.info("Button handler initialized on GPIO %d.", config.BUTTON_PIN)

    def wait_for_press(self, timeout: Optional[float] = None) -> bool:
        """
        Block execution until a button press (falling edge) is detected.

        Args:
            timeout: Optional wait duration in seconds. If None, blocks indefinitely.

        Returns:
            True if the button was pressed, False if the wait timed out.
        """
        timeout_ms = int(timeout * 1000) if timeout else None
        result = GPIO.wait_for_edge(
            config.BUTTON_PIN, 
            GPIO.FALLING,
            bouncetime=200, 
            timeout=timeout_ms
        )
        return result is not None

    def is_pressed(self) -> bool:
        """
        Check the instantaneous state of the button.

        Returns:
            True if the button is currently held down, False otherwise.
        """
        return GPIO.input(config.BUTTON_PIN) == GPIO.LOW

    def set_led(self, on: bool) -> None:
        """
        Activate or deactivate the button's internal LED.

        Args:
            on: True to turn the LED on, False to turn it off.
        """
        state = GPIO.HIGH if on else GPIO.LOW
        GPIO.output(config.BUTTON_LED_PIN, state)

    def cleanup(self) -> None:
        """Release allocated GPIO resources."""
        self.set_led(False)
        GPIO.cleanup()
        logger.info("Button GPIO resources released.")
