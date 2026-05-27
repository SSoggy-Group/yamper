"""
Test: OLED eyes.

Cycles through all eye states for a few seconds each.
Run: python3 -m mimo.test_eyes
"""

import time
from .eyes import EyeDisplay

STATES = ["boot", "idle", "listening", "thinking", "speaking",
          "error", "wifi_error", "sleep"]


def main():
    print("=== Eye animation test ===\n")
    eyes = EyeDisplay()
    eyes.start()

    for state in STATES:
        print(f"  state: {state}")
        eyes.set_state(state)
        time.sleep(3)

    print("\n  done — returning to idle")
    eyes.set_state("idle")
    time.sleep(2)
    eyes.stop()
    print("=== Test complete ===")


if __name__ == "__main__":
    main()
