"""
Yamper — main application.

State machine:
  BOOT → IDLE → LISTENING → THINKING → SPEAKING → IDLE
                   ↓            ↓           ↓
                 ERROR        ERROR       ERROR → IDLE

Run directly:   python3 -m mimo.main
Run via systemd: sudo systemctl start yamper
"""

import signal
import subprocess
import sys
import time

from . import config
from .eyes import EyeDisplay
from .button import ButtonHandler
from . import audio


def check_wifi():
    """Return True if we can reach the internet."""
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", str(config.WIFI_CHECK_TIMEOUT),
             config.WIFI_CHECK_HOST],
            capture_output=True, check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    print("=" * 40)
    print("  Yamper starting up")
    print("=" * 40)

    # ── Initialise hardware ─────────────────────────────────────
    eyes = EyeDisplay()
    eyes.start()
    eyes.set_state("boot")
    time.sleep(1.5)  # let the boot animation play

    button = ButtonHandler()
    conversation_history = []

    # ── Graceful shutdown ───────────────────────────────────────
    running = True

    def shutdown(sig, frame):
        nonlocal running
        print("\n[main] shutting down...")
        running = False

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    # ── Wait for WiFi ───────────────────────────────────────────
    print("[main] checking WiFi...")
    while running and not check_wifi():
        print("[main] no WiFi — retrying...")
        eyes.set_state("wifi_error")
        time.sleep(config.WIFI_RETRY_INTERVAL)

    if not running:
        _cleanup(eyes, button)
        return

    print("[main] WiFi connected")

    # ── Main loop ───────────────────────────────────────────────
    eyes.set_state("idle")
    button.set_led(True)

    while running:
        # Wait for the button press (check every second so we can exit)
        pressed = button.wait_for_press(timeout=1)
        if not pressed:
            continue

        # ── LISTENING ───────────────────────────────────────────
        print("[main] button pressed — listening")
        button.set_led(False)
        eyes.set_state("listening")

        # Small delay so the user has time to start talking
        time.sleep(0.15)

        wav_bytes = audio.record_while_pressed(button.is_pressed)

        if wav_bytes is None:
            print("[main] recording failed")
            eyes.set_state("error")
            time.sleep(2)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        # ── THINKING ────────────────────────────────────────────
        print("[main] thinking...")
        eyes.set_state("thinking")

        # Speech to text
        text = audio.transcribe(wav_bytes)
        if text is None or text == "":
            print("[main] transcription failed or empty")
            eyes.set_state("error")
            time.sleep(2)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        # Get AI response
        reply, conversation_history = audio.chat(text, conversation_history)
        if reply is None:
            print("[main] chat failed")
            eyes.set_state("error")
            time.sleep(2)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        # Text to speech
        mp3_data = audio.text_to_speech(reply)
        if mp3_data is None:
            print("[main] TTS failed")
            eyes.set_state("error")
            time.sleep(2)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        # ── SPEAKING ────────────────────────────────────────────
        print("[main] speaking response")
        eyes.set_state("speaking")
        audio.play_mp3_bytes(mp3_data)

        # ── Back to IDLE ────────────────────────────────────────
        eyes.set_state("idle")
        button.set_led(True)
        print("[main] ready")

    _cleanup(eyes, button)


def _cleanup(eyes, button):
    """Clean up hardware on exit."""
    eyes.set_state("sleep")
    time.sleep(0.5)
    eyes.stop()
    button.cleanup()
    print("[main] goodbye!")


if __name__ == "__main__":
    main()
