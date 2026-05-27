import time
from .eyes import Eyes

def main():
    print("testing screens...")
    eyes = Eyes()
    eyes.start()

    states = ["boot", "idle", "listening", "thinking", "speaking", "error", "wifi_error", "sleep"]
    for s in states:
        print("showing:", s)
        eyes.set_state(s)
        time.sleep(3)

    print("going back to idle")
    eyes.set_state("idle")
    time.sleep(2)
    eyes.stop()
    print("done")

if __name__ == "__main__":
    main()
