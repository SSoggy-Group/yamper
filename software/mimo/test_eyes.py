"""
Diagnostic tool: OLED Displays.

Sequentially activates and renders all defined EyeStates for visual inspection.
"""

import logging
import sys
import time

from .eyes import EyeDisplay, EyeState

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    """Execute the display diagnostic sequence."""
    logger.info("Initializing Display Diagnostic Sequence.")
    eyes = EyeDisplay()
    eyes.start()

    states_to_test = [
        EyeState.BOOT, EyeState.IDLE, EyeState.LISTENING, EyeState.THINKING,
        EyeState.SPEAKING, EyeState.ERROR, EyeState.WIFI_ERROR, EyeState.SLEEP
    ]

    for state in states_to_test:
        logger.info("Rendering state: %s", state.name)
        eyes.set_state(state)
        time.sleep(3.0)

    logger.info("Sequence complete. Restoring IDLE state.")
    eyes.set_state(EyeState.IDLE)
    time.sleep(2.0)
    
    eyes.stop()
    logger.info("Diagnostic completed successfully.")


if __name__ == "__main__":
    main()
