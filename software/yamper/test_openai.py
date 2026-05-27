from . import audio
from . import config

def main():
    print("testing openai api...")
    if not config.OPENAI_API_KEY or config.OPENAI_API_KEY == "sk-your-key-here":
        print("no api key found in config")
        return

    print("asking chatgpt to say hello")
    reply, _ = audio.chat("say hello in one short sentence")
    if not reply:
        print("chat failed")
        return
        
    print("reply:", reply)
    print("converting to speech...")
    
    mp3 = audio.text_to_speech(reply)
    if not mp3:
        print("tts failed")
        return
        
    print("playing audio...")
    audio.play_mp3_bytes(mp3)
    print("done!")

if __name__ == "__main__":
    main()
