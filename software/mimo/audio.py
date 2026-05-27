"""
Yamper audio handling module.

Manages I2S hardware interaction for microphone capture and speaker playback,
and orchestrates communication with the OpenAI API for speech-to-text, 
language modeling, and text-to-speech.
"""

import io
import logging
import wave
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from . import config

logger = logging.getLogger(__name__)

# sounddevice interacts with ALSA for raw PCM streams
try:
    import sounddevice as sd
    SD_AVAILABLE = True
except (ImportError, OSError) as exc:
    SD_AVAILABLE = False
    logger.warning("sounddevice module failed to initialize. Audio hardware is disabled: %s", exc)

# OpenAI Python Client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("openai package not found. AI features disabled.")


# ── Recording Subsystem ───────────────────────────────────────────────────────

def record_while_pressed(
    is_pressed_fn: Callable[[], bool], 
    max_seconds: Optional[float] = None
) -> Optional[bytes]:
    """
    Capture audio stream via ALSA as long as the provided condition function evaluates to True.

    Args:
        is_pressed_fn: A callable returning True while recording should continue.
        max_seconds: The absolute maximum recording duration before forced termination.

    Returns:
        A WAV formatted byte array containing the recorded audio, or None if hardware failed.
    """
    if max_seconds is None:
        max_seconds = float(config.MAX_RECORD_SECONDS)

    if not SD_AVAILABLE:
        logger.error("Recording aborted: sounddevice is not available.")
        return None

    rate = config.MIC_SAMPLE_RATE
    channels = config.MIC_CHANNELS
    chunk_duration = 0.1
    chunk_frames = int(rate * chunk_duration)

    frames: List[np.ndarray] = []
    total_frames = 0
    max_frames = int(rate * max_seconds)

    logger.info("Audio recording initiated.")
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

            if not is_pressed_fn():
                break

        stream.stop()
        stream.close()
    except Exception as exc:
        logger.error("Audio recording stream failed: %s", exc, exc_info=True)
        return None

    if not frames:
        logger.warning("Recording finished but no audio frames were captured.")
        return None

    audio_data = np.concatenate(frames)
    duration = len(audio_data) / rate
    logger.info("Recording complete: %.1f seconds captured.", duration)

    return _to_wav_bytes(audio_data, rate)


def record_seconds(duration: float = 3.0) -> Optional[bytes]:
    """
    Record audio for a fixed duration. Primarily intended for diagnostic testing.

    Args:
        duration: The length of the recording in seconds.

    Returns:
        A WAV formatted byte array, or None if hardware failed.
    """
    if not SD_AVAILABLE:
        logger.error("Recording aborted: sounddevice is not available.")
        return None

    rate = config.MIC_SAMPLE_RATE
    logger.info("Recording fixed duration: %.1f seconds...", duration)
    try:
        data = sd.rec(
            int(rate * duration),
            samplerate=rate,
            channels=config.MIC_CHANNELS,
            dtype=config.MIC_DTYPE,
        )
        sd.wait()
    except Exception as exc:
        logger.error("Fixed duration recording failed: %s", exc, exc_info=True)
        return None

    logger.info("Fixed duration recording complete.")
    return _to_wav_bytes(data, rate)


def _to_wav_bytes(audio_np: np.ndarray, sample_rate: int) -> bytes:
    """Encode a raw PCM numpy array into a WAV byte stream."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(config.MIC_CHANNELS)
        wf.setsampwidth(2)  # 16-bit PCM requires 2 bytes
        wf.setframerate(sample_rate)
        wf.writeframes(audio_np.tobytes())
    buf.seek(0)
    return buf.read()


def save_wav(wav_bytes: bytes, path: str) -> None:
    """Persist WAV bytes to the local filesystem for analysis."""
    try:
        with open(path, "wb") as f:
            f.write(wav_bytes)
        logger.debug("WAV data successfully written to %s.", path)
    except IOError as exc:
        logger.error("Failed to save WAV to %s: %s", path, exc)


# ── Playback Subsystem ────────────────────────────────────────────────────────

def play_wav_bytes(wav_bytes: bytes) -> None:
    """
    Play a WAV byte stream through the ALSA sink. Blocks execution until complete.

    Args:
        wav_bytes: The WAV formatted audio data to play.
    """
    if not SD_AVAILABLE:
        logger.error("Playback aborted: sounddevice is not available.")
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

        logger.info("Initiating playback (%.1fs duration at %d Hz).", len(data) / rate, rate)
        sd.play(data, samplerate=rate)
        sd.wait()
        logger.debug("Playback complete.")
    except Exception as exc:
        logger.error("Hardware playback error: %s", exc, exc_info=True)


def play_mp3_bytes(mp3_bytes: bytes) -> None:
    """
    Play an MP3 byte stream (typically sourced from OpenAI TTS).
    
    Attempts to use pydub for in-memory decoding. If pydub is missing, 
    falls back to a subprocess call utilizing ffmpeg.
    
    Args:
        mp3_bytes: The raw MP3 encoded byte array.
    """
    if not SD_AVAILABLE:
        logger.error("MP3 playback aborted: sounddevice is not available.")
        return

    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        seg = seg.set_channels(1).set_frame_rate(config.TTS_SAMPLE_RATE)
        raw = np.array(seg.get_array_of_samples(), dtype=np.int16)
        
        logger.info("Playing TTS response via pydub decoding.")
        sd.play(raw, samplerate=config.TTS_SAMPLE_RATE)
        sd.wait()
        return
    except ImportError:
        logger.debug("pydub not installed. Falling back to ffmpeg subprocessing for MP3 decode.")

    import os
    import subprocess
    import tempfile

    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
            tmp_mp3.write(mp3_bytes)
            tmp_mp3_name = tmp_mp3.name

        tmp_wav_name = tmp_mp3_name.replace(".mp3", ".wav")
        
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", tmp_mp3_name,
                "-ar", str(config.TTS_SAMPLE_RATE),
                "-ac", "1", "-f", "wav", tmp_wav_name
            ],
            capture_output=True, 
            check=True,
        )

        with open(tmp_wav_name, "rb") as f:
            wav_data = f.read()
            
        play_wav_bytes(wav_data)
        
    except subprocess.CalledProcessError as exc:
        logger.error("FFmpeg fallback decoding failed: %s", exc.stderr.decode())
    except Exception as exc:
        logger.error("Unexpected error during MP3 playback: %s", exc, exc_info=True)
    finally:
        if 'tmp_mp3_name' in locals() and os.path.exists(tmp_mp3_name):
            os.unlink(tmp_mp3_name)
        if 'tmp_wav_name' in locals() and os.path.exists(tmp_wav_name):
            os.unlink(tmp_wav_name)


def play_tone(frequency: float = 440.0, duration: float = 2.0, volume: float = 0.5) -> None:
    """
    Synthesize and play a sine wave tone for hardware validation.

    Args:
        frequency: Frequency of the sine wave in Hz.
        duration: Playback length in seconds.
        volume: Amplitude scale factor (0.0 to 1.0).
    """
    if not SD_AVAILABLE:
        logger.error("Tone playback aborted: sounddevice is not available.")
        return

    rate = config.TTS_SAMPLE_RATE
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    tone = (volume * 32767 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
    
    logger.info("Playing test tone: %d Hz for %.1fs.", int(frequency), duration)
    sd.play(tone, samplerate=rate)
    sd.wait()


# ── OpenAI Integration ────────────────────────────────────────────────────────

def _get_client() -> Optional[OpenAI]:
    """Retrieve an authenticated OpenAI client instance if properly configured."""
    if not OPENAI_AVAILABLE:
        logger.error("Cannot construct OpenAI client: openai module missing.")
        return None
    if not config.OPENAI_API_KEY:
        logger.error("OpenAI API key is missing. Ensure .env is loaded correctly.")
        return None
    return OpenAI(api_key=config.OPENAI_API_KEY)


def transcribe(wav_bytes: bytes) -> Optional[str]:
    """
    Execute speech-to-text inference against the OpenAI Whisper API.

    Args:
        wav_bytes: The WAV formatted audio input.

    Returns:
        The transcribed text string, or None if the API request failed.
    """
    client = _get_client()
    if not client:
        return None

    try:
        buf = io.BytesIO(wav_bytes)
        buf.name = "audio.wav"
        
        logger.debug("Transmitting audio payload to Whisper API.")
        result = client.audio.transcriptions.create(
            model=config.WHISPER_MODEL,
            file=buf,
        )
        text = result.text.strip()
        logger.info("Transcription successful.")
        return text
    except Exception as exc:
        logger.error("Whisper API transcription failed: %s", exc)
        return None


def chat(user_text: str, history: Optional[List[Dict[str, str]]] = None) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    Submit user input to the OpenAI Chat Completions API.

    Maintains contextual awareness by appending system prompts and truncated historical messages.

    Args:
        user_text: The user's transcribed prompt.
        history: Previous conversational messages conforming to the Chat API schema.

    Returns:
        A tuple containing the API's text response and the updated conversation history buffer.
        If the API call fails, returns (None, original_history).
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
        logger.debug("Requesting chat completion from model: %s", config.CHAT_MODEL)
        response = client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=messages,
            max_tokens=200,
        )
        reply = response.choices[0].message.content.strip() if response.choices[0].message.content else ""
        logger.info("Chat completion received.")

        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})

        if len(history) > config.MAX_HISTORY * 2:
            history = history[-(config.MAX_HISTORY * 2):]

        return reply, history
    except Exception as exc:
        logger.error("Chat Completion API failed: %s", exc)
        return None, history


def text_to_speech(text: str) -> Optional[bytes]:
    """
    Convert text into synthesized speech using the OpenAI TTS API.

    Args:
        text: The string to be synthesized.

    Returns:
        The raw MP3 encoded byte stream from the API, or None on failure.
    """
    client = _get_client()
    if not client:
        return None

    try:
        logger.debug("Requesting TTS synthesis from model: %s", config.TTS_MODEL)
        response = client.audio.speech.create(
            model=config.TTS_MODEL,
            voice=config.TTS_VOICE,  # type: ignore
            input=text,
        )
        mp3_bytes = response.content
        logger.info("TTS synthesis successful: %d bytes generated.", len(mp3_bytes))
        return mp3_bytes
    except Exception as exc:
        logger.error("TTS API synthesis failed: %s", exc)
        return None
