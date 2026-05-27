import math
import random
import threading
import time
from PIL import Image, ImageDraw
from . import config

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    has_luma = True
except ImportError:
    has_luma = False
    print("luma.oled not available")

class FakeDisplay:
    width = config.OLED_WIDTH
    height = config.OLED_HEIGHT
    def display(self, img): pass
    def hide(self): pass
    def show(self): pass

def make_device(address):
    if not has_luma:
        return FakeDisplay()
    try:
        return ssd1306(i2c(port=config.I2C_PORT, address=address), width=config.OLED_WIDTH, height=config.OLED_HEIGHT)
    except:
        print("failed to init display at", address)
        return FakeDisplay()

W = config.OLED_WIDTH
H = config.OLED_HEIGHT
CX = W // 2
CY = H // 2

def draw_eye(draw, cx, cy, radius, pupil_radius, open_pct=1.0, look_x=0.0, look_y=0.0):
    rx = radius
    ry = max(2, int(radius * open_pct))
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=1, outline=1)

    px = cx + int(look_x * (radius - pupil_radius) * 0.5)
    py = cy + int(look_y * (ry - pupil_radius) * 0.4)
    draw.ellipse([px - pupil_radius, py - pupil_radius, px + pupil_radius, py + pupil_radius], fill=0)

def frame_idle(t):
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    blink_phase = t % 4.0
    if blink_phase < 0.08: open_pct = 0.15
    elif blink_phase < 0.16: open_pct = 0.15 + (blink_phase - 0.08) / 0.08 * 0.85
    else: open_pct = 1.0

    rng = random.Random(int(t / 5.0))
    draw_eye(draw, CX, CY, 24, 8, open_pct, rng.uniform(-0.3, 0.3), rng.uniform(-0.2, 0.2))
    return img

def frame_listening(t):
    img = Image.new("1", (W, H), 0)
    pulse = 1.0 + 0.08 * math.sin(t * 4)
    draw_eye(ImageDraw.Draw(img), CX, CY, int(26 * pulse), int(6 * pulse), 1.0)
    return img

def frame_thinking(t):
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    draw_eye(draw, CX, CY - 2, 22, 7, 0.85, 0.5, -0.6)
    for i in range(int(t * 2) % 4):
        dx, dy = CX - 12 + i * 10, CY + 26
        draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=1)
    return img

def frame_speaking(t):
    img = Image.new("1", (W, H), 0)
    draw_eye(ImageDraw.Draw(img), CX, int(CY + math.sin(t * 6) * 3), 23, 8, 0.95)
    return img

def frame_error(t):
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    size = 18
    draw.line([CX - size, CY - size, CX + size, CY + size], fill=1, width=3)
    draw.line([CX - size, CY + size, CX + size, CY - size], fill=1, width=3)
    return img

def frame_wifi_error(t):
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    for r in (22, 15, 8):
        draw.arc([CX - r, CY - 4 - r, CX + r, CY - 4 + r], start=225, end=315, fill=1, width=2)
    draw.ellipse([CX - 2, CY - 4 + 8, CX + 2, CY - 4 + 12], fill=1)
    draw.line([CX - 18, CY - 4 + 16, CX + 18, CY - 4 - 18], fill=1, width=2)
    return img

def frame_sleep(t):
    img = Image.new("1", (W, H), 0)
    ImageDraw.Draw(img).line([CX - 22, CY, CX + 22, CY], fill=1, width=2)
    return img

def frame_boot(t):
    img = Image.new("1", (W, H), 0)
    draw_eye(ImageDraw.Draw(img), CX, CY, 24, 8, min(t / 1.5, 1.0))
    return img

frames_map = {
    "idle": frame_idle,
    "listening": frame_listening,
    "thinking": frame_thinking,
    "speaking": frame_speaking,
    "error": frame_error,
    "wifi_error": frame_wifi_error,
    "sleep": frame_sleep,
    "boot": frame_boot,
}

class Eyes:
    def __init__(self):
        self.left = make_device(config.OLED_LEFT_ADDR)
        self.right = make_device(config.OLED_RIGHT_ADDR) if config.OLED_RIGHT_ADDR != config.OLED_LEFT_ADDR else self.left
        self.state = "idle"
        self.state_start = time.monotonic()
        self.running = False
        self.thread = None
        self.lock = threading.Lock()

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread: self.thread.join(timeout=2.0)
        try:
            blank = Image.new("1", (W, H), 0)
            self.left.display(blank)
            if self.right is not self.left:
                self.right.display(blank)
        except: pass

    def set_state(self, state):
        with self.lock:
            if state in frames_map:
                self.state = state
                self.state_start = time.monotonic()

    def loop(self):
        frame_time = 1.0 / 15
        while self.running:
            start = time.monotonic()
            with self.lock:
                state, t = self.state, start - self.state_start

            img = frames_map.get(state, frame_idle)(t)
            try: self.left.display(img)
            except: pass
            
            if self.right is not self.left:
                try: self.right.display(img.transpose(Image.FLIP_LEFT_RIGHT))
                except: pass

            sleep_time = frame_time - (time.monotonic() - start)
            if sleep_time > 0: time.sleep(sleep_time)
