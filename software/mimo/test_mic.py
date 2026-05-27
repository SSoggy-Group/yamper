from . import audio

def main():
    print("testing mic... recording 3s of audio")
    wav = audio.record_seconds(3)
    if not wav:
        print("mic test failed")
        return
    
    audio.save_wav(wav, "test_recording.wav")
    print("playing it back...")
    audio.play_wav_bytes(wav)
    print("done!")

if __name__ == "__main__":
    main()
