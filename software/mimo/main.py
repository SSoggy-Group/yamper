import signal
import subprocess
import sys
import time

from . import audio
from . import config
from .button import Button
from .eyes import Eyes

def check_wifi():
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", str(config.WIFI_CHECK_TIMEOUT), config.WIFI_CHECK_HOST],
            capture_output=True, check=True
        )
        return True
    except:
        return False

def cleanup(eyes, button):
    print("cleaning up hardware...")
    eyes.set_state("sleep")
    time.sleep(0.5)
    eyes.stop()
    button.cleanup()
    print("bye!")

def main():
    print("starting yamper...")

    eyes = Eyes()
    eyes.start()
    eyes.set_state("boot")
    time.sleep(1.5)

    button = Button()
    history = []
    
    running = True

    def on_exit(signum, frame):
        nonlocal running
        print(f"\ngot signal {signum}, stopping...")
        running = False

    signal.signal(signal.SIGTERM, on_exit)
    signal.signal(signal.SIGINT, on_exit)

    print("checking wifi...")
    while running and not check_wifi():
        print(f"no wifi... trying again in {config.WIFI_RETRY_INTERVAL}s")
        eyes.set_state("wifi_error")
        time.sleep(config.WIFI_RETRY_INTERVAL)

    if not running:
        cleanup(eyes, button)
        sys.exit(0)

    print("wifi ok! yamper is ready.")
    eyes.set_state("idle")
    button.set_led(True)

    while running:
        if not button.wait_for_press(timeout=1.0):
            continue

        print("button pressed, listening...")
        button.set_led(False)
        eyes.set_state("listening")
        time.sleep(0.15)
        
        wav_bytes = audio.record_while_pressed(button.is_pressed)

        if not wav_bytes:
            print("audio capture failed :(")
            eyes.set_state("error")
            time.sleep(2.0)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        print("thinking...")
        eyes.set_state("thinking")

        text = audio.transcribe(wav_bytes)
        if not text:
            print("couldn't understand that")
            eyes.set_state("error")
            time.sleep(2.0)
            eyes.set_state("idle")
            button.set_led(True)
            continue
            
        print("user said:", text)
        reply, history = audio.chat(text, history)
        
        if not reply:
            print("llm failed")
            eyes.set_state("error")
            time.sleep(2.0)
            eyes.set_state("idle")
            button.set_led(True)
            continue
            
        print("yamper says:", reply)
        mp3_data = audio.text_to_speech(reply)
        
        if not mp3_data:
            print("tts failed")
            eyes.set_state("error")
            time.sleep(2.0)
            eyes.set_state("idle")
            button.set_led(True)
            continue

        print("speaking...")
        eyes.set_state("speaking")
        audio.play_mp3_bytes(mp3_data)

        eyes.set_state("idle")
        button.set_led(True)
        print("done, back to idle")

    cleanup(eyes, button)

if __name__ == "__main__":
    main()
