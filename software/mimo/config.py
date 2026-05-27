"""
Yamper configuration module.

Provides centralized configuration for hardware pins, I2C addresses,
audio settings, and OpenAI model parameters. Also sets up the default
logging configuration for the application.
"""

import logging
import os
from pathlib import Path
from typing import Final
from dotenv import load_dotenv

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Load .env from the software/ directory (one level up from mimo/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
    logger.debug("Loaded environment variables from %s", _env_path)
else:
    logger.warning("No .env file found at %s. API keys may be missing.", _env_path)

# ── OpenAI Configuration ──────────────────────────────────────────────
OPENAI_API_KEY: Final[str] = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL: Final[str] = "whisper-1"
CHAT_MODEL: Final[str] = "gpt-4o-mini"
TTS_MODEL: Final[str] = "tts-1"
TTS_VOICE: Final[str] = "nova"

SYSTEM_PROMPT: Final[str] = (
    "You are Yamper, a tiny friendly robot. "
    "Keep answers short — one or two sentences is best. "
    "Be cheerful and helpful."
)

MAX_HISTORY: Final[int] = 10

# ── GPIO Configuration ────────────────────────────────────────────────
BUTTON_PIN: Final[int] = 17       # Physical pin 11 — momentary switch to GND
BUTTON_LED_PIN: Final[int] = 27   # Physical pin 13 — LED ring in button

# ── I2C OLED Configuration ────────────────────────────────────────────
OLED_WIDTH: Final[int] = 128
OLED_HEIGHT: Final[int] = 64
OLED_LEFT_ADDR: Final[int] = 0x3C
OLED_RIGHT_ADDR: Final[int] = 0x3D
I2C_PORT: Final[int] = 1

# ── Audio Configuration ───────────────────────────────────────────────
MIC_SAMPLE_RATE: Final[int] = 16000
MIC_CHANNELS: Final[int] = 1
MIC_DTYPE: Final[str] = "int16"

TTS_SAMPLE_RATE: Final[int] = 24000
SPEAKER_CHANNELS: Final[int] = 1

MAX_RECORD_SECONDS: Final[int] = 15
SILENCE_THRESHOLD: Final[int] = 400
SILENCE_DURATION: Final[float] = 1.5

# ── Network Configuration ─────────────────────────────────────────────
WIFI_CHECK_HOST: Final[str] = "8.8.8.8"
WIFI_CHECK_TIMEOUT: Final[int] = 3
WIFI_RETRY_INTERVAL: Final[int] = 10
