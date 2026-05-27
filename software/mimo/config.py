"""
Yamper configuration.

All hardware pins, addresses, and settings live here so you only
need to change one file if your wiring is different.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the software/ directory (one level up from mimo/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ── OpenAI ──────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL = "whisper-1"
CHAT_MODEL = "gpt-4o-mini"
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"

SYSTEM_PROMPT = (
    "You are Yamper, a tiny friendly robot. "
    "Keep answers short — one or two sentences is best. "
    "Be cheerful and helpful."
)

# Maximum conversation history (user + assistant messages kept in memory)
MAX_HISTORY = 10

# ── GPIO pins ───────────────────────────────────────────────────
BUTTON_PIN = 17       # physical pin 11 — momentary switch to GND
BUTTON_LED_PIN = 27   # physical pin 13 — LED ring in button

# ── I2C OLED displays ──────────────────────────────────────────
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_LEFT_ADDR = 0x3C    # left eye
OLED_RIGHT_ADDR = 0x3D   # right eye (change to 0x3C if both are same)
I2C_PORT = 1             # default on Pi Zero 2 W

# ── Audio ───────────────────────────────────────────────────────
MIC_SAMPLE_RATE = 16000       # 16 kHz mono — what Whisper expects
MIC_CHANNELS = 1
MIC_DTYPE = "int16"

TTS_SAMPLE_RATE = 24000       # OpenAI TTS output sample rate
SPEAKER_CHANNELS = 1

# Recording limits
MAX_RECORD_SECONDS = 15       # hard cap even if button held
SILENCE_THRESHOLD = 400       # amplitude below this = silence
SILENCE_DURATION = 1.5        # seconds of silence before auto-stop

# ── WiFi ────────────────────────────────────────────────────────
WIFI_CHECK_HOST = "8.8.8.8"
WIFI_CHECK_TIMEOUT = 3        # seconds
WIFI_RETRY_INTERVAL = 10      # seconds between retries
