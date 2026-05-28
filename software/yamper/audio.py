import io
import wave
import numpy as np
import os
import subprocess
import tempfile
from . import config

try:
    import sounddevice as sd
    has_sd = True
except Exception as e:
    has_sd = False
    print("sounddevice not available:", e)

try:
    from openai import OpenAI
    has_openai = True
except ImportError:
    has_openai = False
    print("openai package missing")

def record_while_pressed(is_pressed_fn, max_seconds=None):
    if max_seconds is None:
        max_seconds = float(config.MAX_RECORD_SECONDS)

    if not has_sd:
        print("can't record, no sounddevice")
        return None

    rate = config.MIC_SAMPLE_RATE
    channels = config.MIC_CHANNELS
    chunk_frames = int(rate * 0.1)
    frames = []
    total_frames = 0
    max_frames = int(rate * max_seconds)

    print("started recording...")
    try:
        stream = sd.InputStream(samplerate=rate, channels=channels, dtype=config.MIC_DTYPE, blocksize=chunk_frames, device=config.MIC_DEVICE_INDEX)
        stream.start()

        while total_frames < max_frames:
            data, _ = stream.read(chunk_frames)
            frames.append(data.copy())
            total_frames += len(data)
            if not is_pressed_fn():
                break

        stream.stop()
        stream.close()
    except Exception as e:
        print("recording failed:", e)
        return None

    if not frames:
        print("no audio captured")
        return None

    audio_data = np.concatenate(frames)
    print(f"done recording: {len(audio_data) / rate:.1f}s")
    
    # save to wav buffer
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio_data.tobytes())
    buf.seek(0)
    return buf.read()

def record_seconds(duration=3.0):
    if not has_sd: return None
    rate = config.MIC_SAMPLE_RATE
    print(f"recording for {duration}s...")
    try:
        data = sd.rec(int(rate * duration), samplerate=rate, channels=config.MIC_CHANNELS, dtype=config.MIC_DTYPE, device=config.MIC_DEVICE_INDEX)
        sd.wait()
        
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(config.MIC_CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(rate)
            wf.writeframes(data.tobytes())
        buf.seek(0)
        return buf.read()
    except Exception as e:
        print("fixed record failed:", e)
        return None

def save_wav(wav_bytes, path):
    try:
        with open(path, "wb") as f:
            f.write(wav_bytes)
    except Exception as e:
        print("failed to save wav:", e)

def play_wav_bytes(wav_bytes):
    if not has_sd: return
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

        sd.play(data, samplerate=rate, device=config.SPEAKER_DEVICE_INDEX)
        sd.wait()
    except Exception as e:
        print("wav play failed:", e)

def play_mp3_bytes(mp3_bytes):
    if not has_sd: return
    
    import sys
    if sys.platform == "darwin":
        tmp_mp3_name = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
                tmp_mp3.write(mp3_bytes)
                tmp_mp3_name = tmp_mp3.name
            subprocess.run(["afplay", tmp_mp3_name], check=True)
            return
        except Exception as e:
            pass
        finally:
            if tmp_mp3_name and os.path.exists(tmp_mp3_name): os.unlink(tmp_mp3_name)

    try:
        from pydub import AudioSegment
        seg = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        seg = seg.set_channels(1).set_frame_rate(config.TTS_SAMPLE_RATE)
        raw = np.array(seg.get_array_of_samples(), dtype=np.int16)
        sd.play(raw, samplerate=config.TTS_SAMPLE_RATE, device=config.SPEAKER_DEVICE_INDEX)
        sd.wait()
        return
    except ImportError:
        pass
    except Exception as e:
        print("pydub failed:", e)
        
    print("falling back to OS player / ffmpeg for mp3")
    tmp_mp3_name = None
    tmp_wav_name = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_mp3:
            tmp_mp3.write(mp3_bytes)
            tmp_mp3_name = tmp_mp3.name

        tmp_wav_name = tmp_mp3_name.replace(".mp3", ".wav")
        subprocess.run(["ffmpeg", "-y", "-i", tmp_mp3_name, "-ar", str(config.TTS_SAMPLE_RATE), "-ac", "1", "-f", "wav", tmp_wav_name], capture_output=True, check=True)

        with open(tmp_wav_name, "rb") as f:
            wav_data = f.read()
        play_wav_bytes(wav_data)
    except Exception as e:
        print("ffmpeg fallback failed:", e)
    finally:
        if tmp_mp3_name and os.path.exists(tmp_mp3_name): os.unlink(tmp_mp3_name)
        if tmp_wav_name and os.path.exists(tmp_wav_name): os.unlink(tmp_wav_name)

def play_tone(frequency=440.0, duration=2.0, volume=0.5):
    if not has_sd: return
    rate = config.TTS_SAMPLE_RATE
    t = np.linspace(0, duration, int(rate * duration), endpoint=False)
    tone = (volume * 32767 * np.sin(2 * np.pi * frequency * t)).astype(np.int16)
    sd.play(tone, samplerate=rate, device=config.SPEAKER_DEVICE_INDEX)
    sd.wait()

def _get_client():
    if config.USE_FREE_AI:
        if not has_openai or not config.HACKCLUB_API_KEY: return None
        return OpenAI(api_key=config.HACKCLUB_API_KEY, base_url="https://ai.hackclub.com/proxy/v1")
    else:
        if not has_openai or not config.OPENAI_API_KEY: return None
        return OpenAI(api_key=config.OPENAI_API_KEY)

def transcribe(wav_bytes):
    if config.USE_FREE_AI:
        try:
            import speech_recognition as sr
            r = sr.Recognizer()
            with sr.AudioFile(io.BytesIO(wav_bytes)) as source:
                audio = r.record(source)
            return r.recognize_google(audio)  # type: ignore
        except Exception as e:
            print("free transcribe failed:", e)
            return None

    client = _get_client()
    if not client: return None
    try:
        buf = io.BytesIO(wav_bytes)
        buf.name = "audio.wav"
        res = client.audio.transcriptions.create(model=config.WHISPER_MODEL, file=buf)
        return res.text.strip()
    except Exception as e:
        print("transcribe failed:", e)
        return None

def chat(user_text, history=None):
    client = _get_client()
    if history is None: history = []
    if not client: return None, history

    msgs = [{"role": "system", "content": config.SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_text}]
    try:
        res = client.chat.completions.create(model=config.CHAT_MODEL, messages=msgs, max_tokens=200)  # type: ignore
        reply = res.choices[0].message.content.strip() if res.choices[0].message.content else ""
        
        history.append({"role": "user", "content": user_text})
        history.append({"role": "assistant", "content": reply})
        if len(history) > config.MAX_HISTORY * 2:
            history = history[-(config.MAX_HISTORY * 2):]
        return reply, history
    except Exception as e:
        print("chat failed:", e)
        return None, history

def text_to_speech(text):
    if config.USE_FREE_AI:
        try:
            from gtts import gTTS
            tts = gTTS(text, lang='en')
            buf = io.BytesIO()
            tts.write_to_fp(buf)
            buf.seek(0)
            return buf.read()
        except Exception as e:
            print("free tts failed:", e)
            return None

    client = _get_client()
    if not client: return None
    try:
        res = client.audio.speech.create(model=config.TTS_MODEL, voice=config.TTS_VOICE, input=text)
        return res.content
    except Exception as e:
        print("tts failed:", e)
        return None
