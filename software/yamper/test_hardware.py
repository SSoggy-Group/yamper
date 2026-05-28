import sys
import time
from . import config
from . import audio
from .eyes import Eyes
from .button import Button

def main():
    print("=== Yamper Hardware Test ===")
    
    # 1. Eyes Test
    print("\n1. Testing OLED Screens...")
    eyes = Eyes()
    eyes.start()
    eyes.set_state("boot")
    time.sleep(2)
    eyes.set_state("idle")
    print("Eyes should be displaying idle animation.")
    
    # 2. Button Test
    print("\n2. Testing Button & LED...")
    button = Button()
    button.set_led(True)
    print("Press the button to continue...")
    button.wait_for_press(timeout=None)
    button.set_led(False)
    print("Button pressed!")

    # 3. Speaker Test
    print("\n3. Testing Speaker...")
    eyes.set_state("speaking")
    audio.play_tone(440, 1.0, 0.5)
    eyes.set_state("idle")
    
    # 4. Microphone Test
    print("\n4. Testing Microphone...")
    print("Hold the button and speak into the microphone (up to 5 seconds)...")
    button.set_led(True)
    button.wait_for_press(timeout=None)
    button.set_led(False)
    
    eyes.set_state("listening")
    wav_bytes = audio.record_while_pressed(button.is_pressed, max_seconds=5.0)
    eyes.set_state("idle")
    
    if wav_bytes:
        print("Playing back recorded audio...")
        eyes.set_state("speaking")
        audio.play_wav_bytes(wav_bytes)
        eyes.set_state("idle")
    else:
        print("Microphone recording failed or was too short.")

    # 5. API Test
    print("\n5. Testing API Connection...")
    if config.USE_FREE_AI:
        has_key = bool(config.HACKCLUB_API_KEY and config.HACKCLUB_API_KEY != "sk-your-key-here")
    else:
        has_key = bool(config.OPENAI_API_KEY and config.OPENAI_API_KEY != "sk-your-key-here")

    if not has_key:
        print("Skipping API test (no valid API key found).")
    else:
        eyes.set_state("thinking")
        print("Sending test message 'say hello in one short sentence' to LLM...")
        reply, _ = audio.chat("say hello in one short sentence")
        if reply:
            print("Reply:", reply)
            eyes.set_state("speaking")
            mp3 = audio.text_to_speech(reply)
            if mp3:
                print("Playing TTS reply...")
                audio.play_mp3_bytes(mp3)
            else:
                print("TTS failed.")
        else:
            print("Chat API failed.")

    # Cleanup
    print("\nTest complete! Cleaning up...")
    eyes.set_state("sleep")
    time.sleep(1)
    eyes.stop()
    button.cleanup()
    print("Done.")

if __name__ == "__main__":
    main()
