"""
Test: push button and LED.

Press and release the button a few times. The LED will light up while held.
Press Ctrl+C to exit.
Run: python3 -m mimo.test_button
"""

import time
from .button import ButtonHandler


def main():
    print("=== Button test ===")
    print("  press the button (Ctrl+C to quit)\n")

    btn = ButtonHandler()
    count = 0

    try:
        while True:
            btn.set_led(False)
            pressed = btn.wait_for_press(timeout=1)
            if not pressed:
                continue

            count += 1
            print(f"  press #{count} detected!")
            btn.set_led(True)

            # Wait for release
            while btn.is_pressed():
                time.sleep(0.05)
            print(f"  released")
            btn.set_led(False)

    except KeyboardInterrupt:
        print("\n\n  stopped by user")
    finally:
        btn.cleanup()

    print("=== Test complete ===")


if __name__ == "__main__":
    main()
