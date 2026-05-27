import time
from .button import Button

def main():
    print("testing button... press ctrl+c to quit")
    btn = Button()
    count = 0
    try:
        while True:
            btn.set_led(False)
            if btn.wait_for_press(1):
                count += 1
                print(f"pressed {count} times!")
                btn.set_led(True)
                while btn.is_pressed():
                    time.sleep(0.05)
                print("released")
    except KeyboardInterrupt:
        print("done")
    finally:
        btn.cleanup()

if __name__ == "__main__":
    main()
