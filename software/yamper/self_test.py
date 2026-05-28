import sys
import time

print("=== Yamper Self Test ===")

# 1. Config Test
try:
    from . import config
    print("[OK] Config loaded")
except Exception as e:
    print(f"[FAIL] Config load failed: {e}")
    sys.exit(1)

# 2. API Key Test
if config.USE_FREE_AI:
    if config.HACKCLUB_API_KEY and config.HACKCLUB_API_KEY != "sk-your-key-here":
        print("[OK] HACKCLUB_API_KEY present")
    else:
        print("[FAIL] HACKCLUB_API_KEY missing")
else:
    if config.OPENAI_API_KEY and config.OPENAI_API_KEY != "sk-your-key-here":
        print("[OK] OPENAI_API_KEY present")
    else:
        print("[FAIL] OPENAI_API_KEY missing")

# 3. Audio Devices List
try:
    import sounddevice as sd
    print("\n--- Audio Devices ---")
    print(sd.query_devices())
    print("---------------------\n")
    print("[OK] Audio devices listed")
except Exception as e:
    print(f"[FAIL] Could not list audio devices: {e}")

# 4. Internet Check
try:
    from . import wifi
    if wifi.internet_ok():
        print("[OK] Internet connection works")
    else:
        print("[FAIL] No internet connection")
except Exception as e:
    print(f"[FAIL] Internet check failed: {e}")

# 5. I2C / OLED
try:
    from . import eyes
    e = eyes.Eyes()
    e.start()
    e.set_state("thinking")
    print("[OK] OLED eyes initialized")
    time.sleep(1)
    e.stop()
except Exception as ex:
    print(f"[FAIL] OLED eyes failed: {ex}")

# 6. Button
try:
    from .button import Button
    b = Button()
    b.set_led(True)
    print("[OK] Button initialized")
    b.cleanup()
except Exception as ex:
    print(f"[FAIL] Button failed: {ex}")

# 7. Speaker beep
try:
    from . import audio
    import numpy as np
    print("Playing beep...")
    if sys.platform != "darwin" and not audio.has_sd:
        print("[SKIP] sounddevice not available, skipping beep")
    else:
        t = np.linspace(0, 1.0, int(config.TTS_SAMPLE_RATE * 1.0), False)
        tone = np.sin(440 * t * 2 * np.pi)
        tone_int16 = (tone * 32767).astype(np.int16)
        sd.play(tone_int16, samplerate=config.TTS_SAMPLE_RATE, blocking=True, device=config.SPEAKER_DEVICE_INDEX)
        print("[OK] Speaker beep played")
except Exception as ex:
    print(f"[FAIL] Speaker beep failed: {ex}")

# 8. Mic record
try:
    print("Recording for 2 seconds...")
    if sys.platform != "darwin" and not audio.has_sd:
        print("[SKIP] sounddevice not available, skipping record")
    else:
        rec = sd.rec(int(2.0 * config.MIC_SAMPLE_RATE), samplerate=config.MIC_SAMPLE_RATE, channels=config.MIC_CHANNELS, dtype=config.MIC_DTYPE, device=config.MIC_DEVICE_INDEX)
        sd.wait()
        print(f"[OK] Recorded {len(rec)} frames")
except Exception as ex:
    print(f"[FAIL] Mic record failed: {ex}")

print("\n=== Test Complete ===")
