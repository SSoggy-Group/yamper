from . import audio

def main():
    print("testing speaker... playing tone for 2s")
    audio.play_tone(440, 2.0, 0.5)
    print("done!")

if __name__ == "__main__":
    main()
