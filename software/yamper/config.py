import os
from dotenv import load_dotenv

# load api keys and stuff
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHISPER_MODEL = "whisper-1"
CHAT_MODEL = "gpt-4o-mini"
TTS_MODEL = "tts-1"
TTS_VOICE = "nova"

SYSTEM_PROMPT = "You are Yamper, a tiny friendly robot. Keep answers short — one or two sentences is best. Be cheerful and helpful."
MAX_HISTORY = 10

# pins
BUTTON_PIN = 17       
BUTTON_LED_PIN = 27   

# displays
OLED_WIDTH = 128
OLED_HEIGHT = 64
OLED_LEFT_ADDR = 0x3C
OLED_RIGHT_ADDR = 0x3D
I2C_PORT = 1

# audio settings
MIC_SAMPLE_RATE = 16000
MIC_CHANNELS = 1
MIC_DTYPE = "int16"

TTS_SAMPLE_RATE = 24000
SPEAKER_CHANNELS = 1

MAX_RECORD_SECONDS = 15
SILENCE_THRESHOLD = 400
SILENCE_DURATION = 1.5

# network
WIFI_CHECK_HOST = "dns.google"
WIFI_CHECK_TIMEOUT = 3
WIFI_RETRY_INTERVAL = 10
