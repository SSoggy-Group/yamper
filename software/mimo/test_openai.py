"""
Test: OpenAI API.

Sends a test message to GPT, converts the reply to speech, and plays it.
Requires a valid OPENAI_API_KEY in software/.env.
Run: python3 -m mimo.test_openai
"""

from . import audio
from . import config


def main():
    print("=== OpenAI API test ===\n")

    # Check API key
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "sk-your-key-here":
        print("  ERROR: set your API key in software/.env first")
        print("  cp ../.env.example .env && nano .env")
        return

    # Test chat
    print("  sending: 'Say hello in one short sentence.'")
    reply, _ = audio.chat("Say hello in one short sentence.")
    if reply is None:
        print("\n  ERROR: chat failed — check your API key and internet")
        return
    print(f"  reply: {reply}\n")

    # Test TTS
    print("  converting to speech...")
    mp3_data = audio.text_to_speech(reply)
    if mp3_data is None:
        print("\n  ERROR: TTS failed")
        return

    print("  playing response...\n")
    audio.play_mp3_bytes(mp3_data)

    print("\n=== Test complete ===")
    print("  if you heard the response, everything works!")


if __name__ == "__main__":
    main()
