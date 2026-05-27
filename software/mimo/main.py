"""
Yamper Application Main Module.

Implements the primary operational state machine for the Yamper hardware,
managing transitions between initialization, idle, listening, processing,
and speaking states, while handling environmental factors like network loss.
"""

import logging
import signal
import subprocess
import sys
import time
from typing import Any, List, Dict

from . import audio
from . import config
from .button import ButtonHandler
from .eyes import EyeDisplay, EyeState

logger = logging.getLogger(__name__)


def check_wifi() -> bool:
    """
    Verify network connectivity by executing a system ping against a known host.

    Returns:
        True if the host is reachable, False otherwise.
    """
    try:
        subprocess.run(
            [
                "ping", "-c", "1", "-W", str(config.WIFI_CHECK_TIMEOUT),
                config.WIFI_CHECK_HOST
            ],
            capture_output=True, 
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _cleanup(eyes: EyeDisplay, button: ButtonHandler) -> None:
    """
    Safely transition hardware into a dormant state before process exit.

    Args:
        eyes: The initialized EyeDisplay component.
        button: The initialized ButtonHandler component.
    """
    logger.info("Executing hardware cleanup sequence.")
    eyes.set_state(EyeState.SLEEP)
    time.sleep(0.5)
    eyes.stop()
    button.cleanup()
    logger.info("Application shutdown complete.")


def main() -> None:
    """Primary application entry point and event loop."""
    logger.info("Initializing Yamper Voice Assistant Core.")

    # ── Initialize Hardware ───────────────────────────────────────────────────
    eyes = EyeDisplay()
    eyes.start()
    eyes.set_state(EyeState.BOOT)
    time.sleep(1.5)

    button = ButtonHandler()
    conversation_history: List[Dict[str, str]] = []
    
    # ── Signal Handling ───────────────────────────────────────────────────────
    running = True

    def shutdown_handler(signum: int, frame: Any) -> None:
        nonlocal running
        logger.info("Received termination signal (%d). Initiating shutdown.", signum)
        running = False

    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)

    # ── Network Verification ──────────────────────────────────────────────────
    logger.info("Verifying network connectivity...")
    while running and not check_wifi():
        logger.warning("Network unreachable. Retrying in %d seconds.", config.WIFI_RETRY_INTERVAL)
        eyes.set_state(EyeState.WIFI_ERROR)
        time.sleep(config.WIFI_RETRY_INTERVAL)

    if not running:
        _cleanup(eyes, button)
        sys.exit(0)

    logger.info("Network connectivity confirmed. System ready.")

    # ── Main Event Loop ───────────────────────────────────────────────────────
    eyes.set_state(EyeState.IDLE)
    button.set_led(True)

    while running:
        pressed = button.wait_for_press(timeout=1.0)
        if not pressed:
            continue

        # ── LISTENING STATE ───────────────────────────────────────────────────
        logger.debug("Input trigger detected. Transitioning to LISTENING state.")
        button.set_led(False)
        eyes.set_state(EyeState.LISTENING)

        time.sleep(0.15)
        wav_bytes = audio.record_while_pressed(button.is_pressed)

        if wav_bytes is None:
            logger.error("Audio capture failed. Aborting interaction cycle.")
            eyes.set_state(EyeState.ERROR)
            time.sleep(2.0)
            eyes.set_state(EyeState.IDLE)
            button.set_led(True)
            continue

        # ── PROCESSING STATE ──────────────────────────────────────────────────
        logger.debug("Audio captured. Transitioning to THINKING state.")
        eyes.set_state(EyeState.THINKING)

        text = audio.transcribe(wav_bytes)
        if not text:
            logger.warning("Transcription yielded no actionable text.")
            eyes.set_state(EyeState.ERROR)
            time.sleep(2.0)
            eyes.set_state(EyeState.IDLE)
            button.set_led(True)
            continue

        reply, conversation_history = audio.chat(text, conversation_history)
        if reply is None:
            logger.error("Language Model inference failed.")
            eyes.set_state(EyeState.ERROR)
            time.sleep(2.0)
            eyes.set_state(EyeState.IDLE)
            button.set_led(True)
            continue

        mp3_data = audio.text_to_speech(reply)
        if mp3_data is None:
            logger.error("Text-to-Speech synthesis failed.")
            eyes.set_state(EyeState.ERROR)
            time.sleep(2.0)
            eyes.set_state(EyeState.IDLE)
            button.set_led(True)
            continue

        # ── SPEAKING STATE ────────────────────────────────────────────────────
        logger.debug("Transitioning to SPEAKING state.")
        eyes.set_state(EyeState.SPEAKING)
        audio.play_mp3_bytes(mp3_data)

        # ── RETURN TO IDLE ────────────────────────────────────────────────────
        eyes.set_state(EyeState.IDLE)
        button.set_led(True)
        logger.debug("Interaction cycle complete. Awaiting input.")

    _cleanup(eyes, button)


if __name__ == "__main__":
    main()
