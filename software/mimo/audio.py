"""
Yamper audio module.

Handles three things:
  1. Recording from the INMP441 I2S microphone
  2. Playing audio through the MAX98357A amplifier
  3. Talking to the OpenAI API (Whisper, Chat, TTS)
"""

import io
import struct
import time
import wave

import numpy as np

from . import config

# sounddevice uses PortAudio which talks to ALSA on the Pi
try:
    import sounddevice as sd
    SD_AVAILABLE = True
except (ImportError, OSError):
    SD_AVAILABLE = False
    print("[audio] sounddevice not available — audio disabled")

# OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("[audio] openai package not available")


# ── Recording ───────────────────────────────────────────────────

def record_while_pressed(is_pressed_fn, max_seconds=None):
    """
    Record audio while is_pressed_fn() returns True.

    Args:
        is_pressed_fn: callable that returns True while button held
        max_seconds:   hard limit (defaults to config.MAX_RECORD_SECONDS)

    Returns:
        WAV file bytes ready to send to Whisper, or None on failure.
    """
    if max_seconds is None:
        max_seconds = config.MAX_RECORD_SECONDS

    if not SD_AVAILABLE:
        print("[audio] cannot record — sounddevice not available")
        return None

    rate = config.MIC_SAMPLE_RATE
    channels = config.MIC_CHANNELS
    chunk_duration = 0.1  # 100 ms chunks
    chunk_frames = int(rate * chunk_duration)

    frames = []
    total_frames = 0
    max_frames = int(rate * max_seconds)

    print("[audio] recording started")
    try:
        stream = sd.InputStream(
            samplerate=rate,
            channels=channels,
            dtype=config.MIC_DTYPE,
            blocksize=chunk_frames,
        )
        stream.start()

        while total_frames < max_frames:
            data, _ = stream.read(chunk_frames)
            frames.append(data.copy())
            total_frames += len(data)

            # Stop when button released
            if not is_pressed_fn():
                break

        stream.stop()
        stream.close()
    except Exception as e:
        print(f"[audio] recording error: {e}")
        return None

    if not frames:
        print("[audio] no audio captured")
        return None

    audio_data = np.concatenate(frames)
    duration = len(audio_data) / rate
    print(f"[audio] recorded {duration:.1f}s ({len(audio_data)} samples)")

    # Convert to WAV bytes
    return _to_wav_bytes(audio_data, rate)


def record_seconds(duration=3):
    """
    Record a fixed number of seconds. Useful for testing.
    Returns WAV file bytes or None.
    """
    if not SD_AVAILABLE:
        print("[audio] cannot record — sounddevice not available")
        return None

    rate = config.MIC_SAMPLE_RATE
    print(f"[audio] recording {duration}s ...")
    try:
        data = sd.rec(
            int(rate * duration),
            samplerate=rate,
            channels=config.MIC_CHANNELS,
            dtype=config.MIC_DTYPE,
        )
        sd.wait()
    except Exception as e:
        print(f"[audio] recording error: {e}")
        return None

    print(f"[audio] recorded {duration}s")
    return _to_wav_bytes(data, rate)


def _to_wav_bytes(audio_np, sample_rate):
    """Convert a numpy int16 array to in-memory WAV file bytes."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(config.MIC_CHANNELS)
        wf.setsampwidth(2)  # 16-bit = 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio_np.tobytes())
    buf.seek(0)
    return buf.read()


def save_wav(wav_bytes, path):
    """Save WAV bytes to a file (for testing)."""
    with open(path, "wb") as f:
        f.write(wav_bytes)
    print(f"[audio] saved to {path}")


# ── Playback ────────────────────────────────────────────────────

def play_wav_bytes(wav_bytes):
    """Play WAV data through the speaker. Blocks until done."""
    if not SD_AVAILABLE:
        print("[audio] cannot play — sounddevice not available")
        return

    try:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            rate = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
            dtype = "int16" if wf.getsampwidth() == 2 else "int32"

        data = np.frombuffer(frames, dtype=dtype)
        if channels > 1:
            data = data.reshape(-1, channels)

        print(f"[audio] playing {len(data)/rate:.1f}s audio")
        sd.play(data, samplerate=rate)
        sd.wait()
        print("[audio] playback done")
    except Exception as e:
        print(f"[audio] playback error: {e}")


def play_mp3_bytes(mp3_bytes):
    """
    Play MP3 data from OpenAI TTS.
    Converts MP3 to WAV using a simple approach — if pydub is available
    we use it, otherwise we write to a temp file and use ffmpeg.
    """
    if not SD_AVAILABLE:
        print("[audio] cannot play — sounddevice not available")
        return

    try:
        # Try pydub first (optional dependency)
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        seg = seg.set_channels(1).set_frame_rate(config.TTS_SAMPLE_RATE)
        raw = np.array(seg.get_array_of_samples(), dtype=np.int16)
        print(f"[audio] playing TTS ({len(raw)/config.TTS_SAMPLE_RATE:.1f}s)")
        sd.play(raw, samplerate=config.TTS_SAMPLE_RATE)
        sd.wait()
        print("[audio] TTS playback done")
        return
    except ImportError:
        pass

    # Fallback: use subprocess + ffmpeg to decode MP3
    import subprocess
    import tempfile
    import os
    try:
        tmp_mp3 = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        tmp_mp3.write(mp3_bytes)
        tmp_mp3.close()

        tmp_wav = tmp_mp3.name.replace(".mp3", ".wav")
        subprocess.run(
            ["ffmpeg", "-y", "-i", tmp_mp3.name,
             "-ar", str(config.TTS_SAMPLE_RATE),
             "-ac", "1", "-f", "wav", tmp_wav],
            capture_output=True, check=True,
        )

        with open(tmp_wav, "rb") as f:
            play_wav_bytes(f.read())

        os.unlink(tmp_mp3.name)
        os.unlink(tmp_wav)
    except Exception as e:
        print(f"[audio] MP3 decode/playback error: {e}")


def play_tone(frequency=440, duration=2.0, volume=0.5):
    """Play a sine wave tone. Useful for testing the speaker."""
    if not SD_AVAILABLE:
        print("[audio] cannot play — sounddevice not available")
        return

    rate = config.TTS_SAMPLE_RATE
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    tone = (volume * 32767 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
    print(f"[audio] playing {frequency}Hz tone for {duration}s")
    sd.play(tone, samplerate=rate)
    sd.wait()
    print("[audio] tone done")


# ── OpenAI API ──────────────────────────────────────────────────

def _get_client():
    """Create an OpenAI client. Returns None if not configured."""
    if not OPENAI_AVAILABLE:
        print("[audio] openai package not installed")
        return None
    if not config.OPENAI_API_KEY:
        print("[audio] OPENAI_API_KEY not set — check your .env file")
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


def transcribe(wav_bytes):
    """
    Send WAV audio to OpenAI Whisper for speech-to-text.
    Returns the transcribed text, or None on failure.
    """
    client = _get_client()
    if not client:
        return None

    try:
        buf = io.BytesIO(wav_bytes)
        buf.name = "audio.wav"  # OpenAI needs a filename
        result = client.audio.transcriptions.create(
            model=config.WHISPER_MODEL,
            file=buf,
        )
        text = result.text.strip()
        print(f"[audio] transcribed: {text}")
        return text
    except Exception as e:
        print(f"[audio] Whisper error: {e}")
        return None


def chat(user_text, history=None):
    """
    Send text to GPT and get a response.

    Args:
        user_text: what the user said
        history:   list of {"role": ..., "content": ...} dicts

    Returns:
        (response_text, updated_history) or (None, history) on failure
    """
    client = _get_client()
    if not client:
        return None, history or []

    if history is None:
        history = []

    messages = [{"role": "system", "content": config.SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=messages,
            max_tokens=200,
        )
        reply = response.choices[0].message.content.strip()
        print(f"[audio] GPT reply: {reply}")

        # Update history
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})

        # Trim history to keep memory usage low
        if len(history) > config.MAX_HISTORY * 2:
            history = history[-(config.MAX_HISTORY * 2):]

        return reply, history
    except Exception as e:
        print(f"[audio] GPT error: {e}")
        return None, history


def text_to_speech(text):
    """
    Convert text to speech using OpenAI TTS.
    Returns MP3 bytes, or None on failure.
    """
    client = _get_client()
    if not client:
        return None

    try:
        response = client.audio.speech.create(
            model=config.TTS_MODEL,
            voice=config.TTS_VOICE,
            input=text,
        )
        mp3_bytes = response.content
        print(f"[audio] TTS: got {len(mp3_bytes)} bytes of audio")
        return mp3_bytes
    except Exception as e:
        print(f"[audio] TTS error: {e}")
        return None
