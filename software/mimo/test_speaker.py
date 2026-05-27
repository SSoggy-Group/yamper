"""
Test: speaker playback.

Plays a 440 Hz sine wave for 2 seconds through the MAX98357A amplifier.
Run: python3 -m mimo.test_speaker
"""

from . import audio


def main():
    print("=== Speaker test ===\n")
    print("  playing 440 Hz tone for 2 seconds...")

    audio.play_tone(frequency=440, duration=2.0, volume=0.5)

    print("\n  if you heard a tone, the speaker works!")
    print("  if not, check:")
    print("    - MAX98357A wiring")
    print("    - speaker connections")
    print("    - I2S overlay in /boot/config.txt")
    print("\n=== Test complete ===")


if __name__ == "__main__":
    main()
