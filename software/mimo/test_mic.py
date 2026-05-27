"""
Test: microphone recording.

Records 3 seconds of audio, saves to test_recording.wav, then plays it back.
Run: python3 -m mimo.test_mic
"""

from . import audio


def main():
    print("=== Microphone test ===\n")
    print("  recording 3 seconds — speak now!")

    wav_bytes = audio.record_seconds(duration=3)

    if wav_bytes is None:
        print("\n  ERROR: recording failed")
        print("  check that the INMP441 is wired and I2S is enabled")
        return

    audio.save_wav(wav_bytes, "test_recording.wav")
    print("\n  playing back...")
    audio.play_wav_bytes(wav_bytes)

    print("\n=== Test complete ===")
    print("  saved: test_recording.wav")


if __name__ == "__main__":
    main()
