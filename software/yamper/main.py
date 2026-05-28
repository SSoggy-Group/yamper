import signal
import subprocess
import sys
import time

from . import audio
from . import config
from . import wifi
from . import wifi_setup
from .button import Button
from .eyes import Eyes



def cleanup(eyes, button):
    print("cleaning up hardware...")
    eyes.set_state("sleep")
    time.sleep(0.5)
    eyes.stop()
    button.cleanup()
    print("bye!")

def process_audio_interaction(eyes, button, history):
    print("button pressed, listening...")
    button.set_led(False)
    eyes.set_state("listening")
    time.sleep(0.15)
    
    press_start = time.time()
    shutdown_requested = [False]

    def check_button():
        if not button.is_pressed():
            return False
        if time.time() - press_start >= config.SHUTDOWN_HOLD_SECONDS:
            shutdown_requested[0] = True
            return False
        return True

    wav_bytes = audio.record_while_pressed(check_button)
    
    if shutdown_requested[0]:
        return "SHUTDOWN"

    if not wav_bytes:
        print("audio capture failed :(")
        eyes.set_state("error")
        time.sleep(2.0)
        eyes.set_state("idle")
        button.set_led(True)
        return history

    print("thinking...")
    eyes.set_state("thinking")

    text = audio.transcribe(wav_bytes)
    if not text:
        print("couldn't understand that")
        eyes.set_state("error")
        time.sleep(2.0)
        eyes.set_state("idle")
        button.set_led(True)
        return history
        
    print("user said:", text)
    reply, history = audio.chat(text, history)
    
    if not reply:
        print("llm failed")
        eyes.set_state("error")
        time.sleep(2.0)
        eyes.set_state("idle")
        button.set_led(True)
        return history
        
    print("yamper says:", reply)
    mp3_data = audio.text_to_speech(reply)
    
    if not mp3_data:
        print("tts failed")
        eyes.set_state("error")
        time.sleep(2.0)
        eyes.set_state("idle")
        button.set_led(True)
        return history

    print("speaking...")
    eyes.set_state("speaking")
    audio.play_mp3_bytes(mp3_data)

    eyes.set_state("idle")
    button.set_led(True)
    print("done, back to idle")
    return history


def check_force_setup(button):
    if not button.is_pressed():
        return False
    print(f"button is held, waiting {config.WIFI_SETUP_FORCE_HOLD_SECONDS}s to check for force setup...")
    start_hold = time.time()
    while button.is_pressed():
        if time.time() - start_hold >= config.WIFI_SETUP_FORCE_HOLD_SECONDS:
            print("force setup triggered!")
            return True
        time.sleep(0.1)
    return False

def handle_wifi_setup(eyes, force_setup, is_running_func):
    if is_running_func():
        print("checking internet...")
    internet_working = wifi.internet_ok()

    while is_running_func() and (force_setup or not internet_working):
        if force_setup:
            print("force setup requested.")
        else:
            print("no internet, entering setup mode...")
            
        success = wifi_setup.run_setup_mode(eyes)
        if success:
            force_setup = False
            print("setup complete, checking internet again...")
            internet_working = wifi.internet_ok()
        else:
            print("setup mode failed or aborted, retrying in a moment...")
            time.sleep(2)


def run_robot():
    print("starting yamper...")

    eyes = Eyes()
    eyes.start()
    eyes.set_state("boot")
    time.sleep(1.5)

    if not audio.has_sd and sys.platform != "darwin":
        print("WARNING: sounddevice not found! Audio will not work.")

    if config.USE_FREE_AI:
        if not config.HACKCLUB_API_KEY or config.HACKCLUB_API_KEY == "sk-your-key-here":
            print("ERROR: HACKCLUB_API_KEY is not set in config/environment.")
            eyes.set_state("error")
            time.sleep(5)
            eyes.stop()
            sys.exit(1)
    else:
        if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "sk-your-key-here":
            print("ERROR: OPENAI_API_KEY is not set in config/environment.")
            eyes.set_state("error")
            time.sleep(5)
            eyes.stop()
            sys.exit(1)

    button = Button()
    history = []
    
    running = True

    def on_exit(signum, frame):
        nonlocal running
        print(f"\ngot signal {signum}, stopping...")
        running = False

    import threading
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, on_exit)
        signal.signal(signal.SIGINT, on_exit)

    force_setup = check_force_setup(button)
    handle_wifi_setup(eyes, force_setup, lambda: running)

    if not running:
        cleanup(eyes, button)
        sys.exit(0)

    print("wifi ok! yamper is ready.")
    eyes.set_state("idle")
    button.set_led(True)

    while running:
        if not button.wait_for_press(timeout=1.0):
            continue

        res = process_audio_interaction(eyes, button, history)
        if res == "SHUTDOWN":
            print("long press detected! initiating shutdown...")
            eyes.set_state("sleep")
            time.sleep(1.0)
            subprocess.run(["sudo", "shutdown", "-h", "now"])
            running = False
            break
        else:
            history = res

    cleanup(eyes, button)

def main():
    if sys.platform == "darwin":
        import threading
        print("initializing mac screens...")
        from . import eyes
        eyes.make_device(config.OLED_LEFT_ADDR)
        
        t = threading.Thread(target=run_robot, daemon=True)
        t.start()
        
        try:
            while t.is_alive():
                if hasattr(eyes, '_tk_root') and eyes._tk_root is not None:
                    try: eyes._tk_root.pump_gui()
                    except Exception: break
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("\nstopping...")
    else:
        run_robot()

if __name__ == "__main__":
    main()
