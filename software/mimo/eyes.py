"""
Yamper OLED eye animations.

Drives one or two SSD1306 128x64 OLED displays over I2C using luma.oled.
Each eye state is drawn with Pillow — the animation thread redraws at ~15 FPS.
If only one display is found, both eyes show on the same screen.
"""

import math
import random
import threading
import time

from PIL import Image, ImageDraw

from . import config

# Try to import luma — if running on a non-Pi machine the tests will
# still work in "headless" mode with a stub.
try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    LUMA_AVAILABLE = True
except ImportError:
    LUMA_AVAILABLE = False


# ── Display wrapper ─────────────────────────────────────────────

class _DisplayStub:
    """Fake display for testing on a laptop."""
    width = config.OLED_WIDTH
    height = config.OLED_HEIGHT

    def display(self, image):
        pass

    def hide(self):
        pass

    def show(self):
        pass


def _make_device(address):
    """Create a luma ssd1306 device or return a stub."""
    if not LUMA_AVAILABLE:
        print(f"[eyes] luma.oled not available — using stub for 0x{address:02X}")
        return _DisplayStub()
    try:
        serial = i2c(port=config.I2C_PORT, address=address)
        device = ssd1306(serial, width=config.OLED_WIDTH, height=config.OLED_HEIGHT)
        print(f"[eyes] OLED found at 0x{address:02X}")
        return device
    except Exception as e:
        print(f"[eyes] could not open OLED at 0x{address:02X}: {e}")
        return _DisplayStub()


# ── Drawing helpers ─────────────────────────────────────────────

W = config.OLED_WIDTH    # 128
H = config.OLED_HEIGHT   # 64
CX = W // 2              # center x
CY = H // 2              # center y


def _draw_eye(draw, cx, cy, radius, pupil_radius, open_pct=1.0,
              look_x=0, look_y=0):
    """Draw one round eye with eyelids and pupil offset."""
    # Outer eye (white ellipse)
    rx = radius
    ry = int(radius * open_pct)
    if ry < 2:
        ry = 2
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=1, outline=1)

    # Pupil (filled black circle offset by look direction)
    px = cx + int(look_x * (radius - pupil_radius) * 0.5)
    py = cy + int(look_y * (ry - pupil_radius) * 0.4)
    draw.ellipse(
        [px - pupil_radius, py - pupil_radius,
         px + pupil_radius, py + pupil_radius],
        fill=0,
    )


def _draw_x_eye(draw, cx, cy, size):
    """Draw an X-shaped error eye."""
    draw.line([cx - size, cy - size, cx + size, cy + size], fill=1, width=3)
    draw.line([cx - size, cy + size, cx + size, cy - size], fill=1, width=3)


def _draw_wifi_icon(draw, cx, cy):
    """Draw a simple 'no WiFi' symbol."""
    # Three arcs for wifi signal
    for r in (22, 15, 8):
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.arc(bbox, start=225, end=315, fill=1, width=2)
    # Small dot at bottom
    draw.ellipse([cx - 2, cy + 8, cx + 2, cy + 12], fill=1)
    # Slash across the whole thing
    draw.line([cx - 18, cy + 16, cx + 18, cy - 18], fill=1, width=2)


# ── Eye state renderers ────────────────────────────────────────

def _frame_idle(t):
    """Idle: big round eyes, periodic blink, random look."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    # Blink every 3-5 seconds for ~0.15s
    blink_cycle = 4.0
    blink_phase = t % blink_cycle
    if blink_phase < 0.08:
        open_pct = 0.15
    elif blink_phase < 0.16:
        open_pct = 0.15 + (blink_phase - 0.08) / 0.08 * 0.85
    else:
        open_pct = 1.0

    # Slow random look direction (changes every ~5 seconds)
    look_seed = int(t / 5.0)
    rng = random.Random(look_seed)
    look_x = rng.uniform(-0.3, 0.3)
    look_y = rng.uniform(-0.2, 0.2)

    _draw_eye(draw, CX, CY, radius=24, pupil_radius=8,
              open_pct=open_pct, look_x=look_x, look_y=look_y)
    return img


def _frame_listening(t):
    """Listening: eyes widen, pupils dilate, subtle pulse."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    # Pulsing radius
    pulse = 1.0 + 0.08 * math.sin(t * 4)
    radius = int(26 * pulse)
    pupil_r = int(6 * pulse)

    _draw_eye(draw, CX, CY, radius=radius, pupil_radius=pupil_r,
              open_pct=1.0)
    return img


def _frame_thinking(t):
    """Thinking: eyes look up-right, dots animate."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    _draw_eye(draw, CX, CY - 2, radius=22, pupil_radius=7,
              open_pct=0.85, look_x=0.5, look_y=-0.6)

    # Animated dots below the eye
    num_dots = int(t * 2) % 4
    for i in range(num_dots):
        dx = CX - 12 + i * 10
        dy = CY + 26
        draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=1)

    return img


def _frame_speaking(t):
    """Speaking: normal eyes with vertical bounce."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    bounce = math.sin(t * 6) * 3
    _draw_eye(draw, CX, int(CY + bounce), radius=23, pupil_radius=8,
              open_pct=0.95)
    return img


def _frame_error(t):
    """Error: X-shaped eyes."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    _draw_x_eye(draw, CX, CY, size=18)
    return img


def _frame_wifi_error(t):
    """WiFi error: no-WiFi icon."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    _draw_wifi_icon(draw, CX, CY - 4)
    return img


def _frame_sleep(t):
    """Sleep: closed eyes (flat lines)."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    y = CY
    draw.line([CX - 22, y, CX + 22, y], fill=1, width=2)
    return img


def _frame_boot(t):
    """Boot: eyes open from closed."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    # Open over 1.5 seconds
    progress = min(t / 1.5, 1.0)
    open_pct = progress
    _draw_eye(draw, CX, CY, radius=24, pupil_radius=8,
              open_pct=open_pct)
    return img


# Map state names to frame functions
_STATE_FRAMES = {
    "idle": _frame_idle,
    "listening": _frame_listening,
    "thinking": _frame_thinking,
    "speaking": _frame_speaking,
    "error": _frame_error,
    "wifi_error": _frame_wifi_error,
    "sleep": _frame_sleep,
    "boot": _frame_boot,
}


# ── EyeDisplay controller ──────────────────────────────────────

class EyeDisplay:
    """
    Controls both OLED eye displays.

    Usage:
        eyes = EyeDisplay()
        eyes.start()
        eyes.set_state("idle")
        ...
        eyes.stop()
    """

    def __init__(self):
        self._left = _make_device(config.OLED_LEFT_ADDR)
        # Only try the second address if it differs
        if config.OLED_RIGHT_ADDR != config.OLED_LEFT_ADDR:
            self._right = _make_device(config.OLED_RIGHT_ADDR)
        else:
            self._right = self._left
            print("[eyes] both eyes on same address — mirroring")

        self._state = "idle"
        self._state_start = time.monotonic()
        self._running = False
        self._thread = None
        self._lock = threading.Lock()

    def start(self):
        """Start the animation thread."""
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("[eyes] animation started")

    def stop(self):
        """Stop the animation thread and blank the displays."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
        try:
            blank = Image.new("1", (W, H), 0)
            self._left.display(blank)
            if self._right is not self._left:
                self._right.display(blank)
        except Exception:
            pass
        print("[eyes] animation stopped")

    def set_state(self, state):
        """Switch to a new eye state. Resets the animation timer."""
        with self._lock:
            if state in _STATE_FRAMES:
                self._state = state
                self._state_start = time.monotonic()
            else:
                print(f"[eyes] unknown state: {state}")

    def get_state(self):
        """Return the current state name."""
        with self._lock:
            return self._state

    def _loop(self):
        """Render frames at ~15 FPS."""
        fps = 15
        frame_time = 1.0 / fps

        while self._running:
            start = time.monotonic()

            with self._lock:
                state = self._state
                t = start - self._state_start

            frame_fn = _STATE_FRAMES.get(state, _frame_idle)
            img = frame_fn(t)

            # The left eye gets the image as-is
            try:
                self._left.display(img)
            except Exception:
                pass

            # The right eye gets a horizontally flipped copy
            # (so the pupils mirror naturally, like real eyes)
            if self._right is not self._left:
                try:
                    self._right.display(img.transpose(Image.FLIP_LEFT_RIGHT))
                except Exception:
                    pass

            elapsed = time.monotonic() - start
            sleep_for = frame_time - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
