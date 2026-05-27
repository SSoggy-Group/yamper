"""
Yamper OLED eye animations module.

Provides a threaded interface to render various eye states on one or two
SSD1306 128x64 OLED displays via the I2C bus using the luma.oled library.
"""

import enum
import logging
import math
import random
import threading
import time
from typing import Any, Callable, Dict

from PIL import Image, ImageDraw

from . import config

logger = logging.getLogger(__name__)

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    LUMA_AVAILABLE = True
except ImportError:
    LUMA_AVAILABLE = False


class EyeState(enum.Enum):
    """Enumeration of all supported eye animation states."""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"
    ERROR = "error"
    WIFI_ERROR = "wifi_error"
    SLEEP = "sleep"
    BOOT = "boot"


class _DisplayStub:
    """Fallback stub for non-Raspberry Pi environments."""
    width: int = config.OLED_WIDTH
    height: int = config.OLED_HEIGHT

    def display(self, image: Image.Image) -> None:
        """Mock method for rendering an image."""
        pass

    def hide(self) -> None:
        """Mock method for hiding the display."""
        pass

    def show(self) -> None:
        """Mock method for showing the display."""
        pass


def _make_device(address: int) -> Any:
    """
    Initialize a luma ssd1306 device or return a stub if unavailable.

    Args:
        address: The I2C address of the display.

    Returns:
        An initialized display device or a stub.
    """
    if not LUMA_AVAILABLE:
        logger.debug("luma.oled not available. Using stub for display at 0x%02X", address)
        return _DisplayStub()
    try:
        serial = i2c(port=config.I2C_PORT, address=address)
        device = ssd1306(serial, width=config.OLED_WIDTH, height=config.OLED_HEIGHT)
        logger.info("Successfully initialized OLED display at 0x%02X", address)
        return device
    except Exception as exc:
        logger.error("Failed to initialize OLED at 0x%02X: %s", address, exc)
        return _DisplayStub()


# ── Drawing Helpers ───────────────────────────────────────────────────────────

W: int = config.OLED_WIDTH
H: int = config.OLED_HEIGHT
CX: int = W // 2
CY: int = H // 2


def _draw_eye(
    draw: ImageDraw.ImageDraw,
    cx: int,
    cy: int,
    radius: int,
    pupil_radius: int,
    open_pct: float = 1.0,
    look_x: float = 0.0,
    look_y: float = 0.0
) -> None:
    """
    Draw a single rounded eye with eyelids and pupil offset.

    Args:
        draw: The Pillow ImageDraw context.
        cx: Center X coordinate.
        cy: Center Y coordinate.
        radius: Base radius of the eye.
        pupil_radius: Radius of the inner pupil.
        open_pct: Percentage the eye is open (0.0 to 1.0).
        look_x: Horizontal gaze offset (-1.0 to 1.0).
        look_y: Vertical gaze offset (-1.0 to 1.0).
    """
    rx = radius
    ry = max(2, int(radius * open_pct))
    
    # Outer white ellipse
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=1, outline=1)

    # Inner black pupil
    px = cx + int(look_x * (radius - pupil_radius) * 0.5)
    py = cy + int(look_y * (ry - pupil_radius) * 0.4)
    draw.ellipse(
        [px - pupil_radius, py - pupil_radius, px + pupil_radius, py + pupil_radius],
        fill=0,
    )


def _draw_x_eye(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    """Draw an X-shaped indicator for error states."""
    draw.line([cx - size, cy - size, cx + size, cy + size], fill=1, width=3)
    draw.line([cx - size, cy + size, cx + size, cy - size], fill=1, width=3)


def _draw_wifi_icon(draw: ImageDraw.ImageDraw, cx: int, cy: int) -> None:
    """Draw a stylized no-WiFi symbol."""
    for r in (22, 15, 8):
        bbox = [cx - r, cy - r, cx + r, cy + r]
        draw.arc(bbox, start=225, end=315, fill=1, width=2)
    draw.ellipse([cx - 2, cy + 8, cx + 2, cy + 12], fill=1)
    draw.line([cx - 18, cy + 16, cx + 18, cy - 18], fill=1, width=2)


# ── Frame Renderers ───────────────────────────────────────────────────────────

def _frame_idle(t: float) -> Image.Image:
    """Render the IDLE state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    blink_cycle = 4.0
    blink_phase = t % blink_cycle
    if blink_phase < 0.08:
        open_pct = 0.15
    elif blink_phase < 0.16:
        open_pct = 0.15 + (blink_phase - 0.08) / 0.08 * 0.85
    else:
        open_pct = 1.0

    look_seed = int(t / 5.0)
    rng = random.Random(look_seed)
    look_x = rng.uniform(-0.3, 0.3)
    look_y = rng.uniform(-0.2, 0.2)

    _draw_eye(draw, CX, CY, radius=24, pupil_radius=8, open_pct=open_pct, look_x=look_x, look_y=look_y)
    return img


def _frame_listening(t: float) -> Image.Image:
    """Render the LISTENING state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    pulse = 1.0 + 0.08 * math.sin(t * 4)
    radius = int(26 * pulse)
    pupil_r = int(6 * pulse)

    _draw_eye(draw, CX, CY, radius=radius, pupil_radius=pupil_r, open_pct=1.0)
    return img


def _frame_thinking(t: float) -> Image.Image:
    """Render the THINKING state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    _draw_eye(draw, CX, CY - 2, radius=22, pupil_radius=7, open_pct=0.85, look_x=0.5, look_y=-0.6)

    num_dots = int(t * 2) % 4
    for i in range(num_dots):
        dx = CX - 12 + i * 10
        dy = CY + 26
        draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=1)

    return img


def _frame_speaking(t: float) -> Image.Image:
    """Render the SPEAKING state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)

    bounce = math.sin(t * 6) * 3
    _draw_eye(draw, CX, int(CY + bounce), radius=23, pupil_radius=8, open_pct=0.95)
    return img


def _frame_error(t: float) -> Image.Image:
    """Render the ERROR state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    _draw_x_eye(draw, CX, CY, size=18)
    return img


def _frame_wifi_error(t: float) -> Image.Image:
    """Render the WIFI_ERROR state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    _draw_wifi_icon(draw, CX, CY - 4)
    return img


def _frame_sleep(t: float) -> Image.Image:
    """Render the SLEEP state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    draw.line([CX - 22, CY, CX + 22, CY], fill=1, width=2)
    return img


def _frame_boot(t: float) -> Image.Image:
    """Render the BOOT state frame."""
    img = Image.new("1", (W, H), 0)
    draw = ImageDraw.Draw(img)
    open_pct = min(t / 1.5, 1.0)
    _draw_eye(draw, CX, CY, radius=24, pupil_radius=8, open_pct=open_pct)
    return img


_STATE_FRAMES: Dict[EyeState, Callable[[float], Image.Image]] = {
    EyeState.IDLE: _frame_idle,
    EyeState.LISTENING: _frame_listening,
    EyeState.THINKING: _frame_thinking,
    EyeState.SPEAKING: _frame_speaking,
    EyeState.ERROR: _frame_error,
    EyeState.WIFI_ERROR: _frame_wifi_error,
    EyeState.SLEEP: _frame_sleep,
    EyeState.BOOT: _frame_boot,
}


class EyeDisplay:
    """
    Manages the threaded rendering and hardware integration for the OLED eyes.
    
    Supports dual-display mirroring if both displays share the same I2C address,
    or independent left/right rendering if they possess distinct addresses.
    """

    def __init__(self) -> None:
        self._left = _make_device(config.OLED_LEFT_ADDR)
        
        if config.OLED_RIGHT_ADDR != config.OLED_LEFT_ADDR:
            self._right = _make_device(config.OLED_RIGHT_ADDR)
        else:
            self._right = self._left
            logger.info("OLED addresses identical; defaulting to mirrored mode.")

        self._state: EyeState = EyeState.IDLE
        self._state_start: float = time.monotonic()
        self._running: bool = False
        self._thread: threading.Thread | None = None
        self._lock: threading.Lock = threading.Lock()

    def start(self) -> None:
        """Start the background animation thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True, name="EyeDisplayThread")
        self._thread.start()
        logger.info("Eye display animation thread started.")

    def stop(self) -> None:
        """Stop the background animation thread and clear the displays."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        try:
            blank = Image.new("1", (W, H), 0)
            self._left.display(blank)
            if self._right is not self._left:
                self._right.display(blank)
        except Exception as exc:
            logger.warning("Failed to blank displays during stop: %s", exc)
        logger.info("Eye display animation thread stopped.")

    def set_state(self, state: EyeState) -> None:
        """
        Transition the eyes to a new state and reset the animation timer.

        Args:
            state: The target EyeState.
        """
        with self._lock:
            if state in _STATE_FRAMES:
                self._state = state
                self._state_start = time.monotonic()
                logger.debug("Transitioned eye state to: %s", state.name)
            else:
                logger.error("Attempted to set unmapped EyeState: %s", state)

    def get_state(self) -> EyeState:
        """Retrieve the current eye state."""
        with self._lock:
            return self._state

    def _loop(self) -> None:
        """Main rendering loop executed by the animation thread."""
        fps = 15
        frame_time = 1.0 / fps

        while self._running:
            start_time = time.monotonic()

            with self._lock:
                state = self._state
                t = start_time - self._state_start

            frame_fn = _STATE_FRAMES.get(state, _frame_idle)
            img = frame_fn(t)

            try:
                self._left.display(img)
            except Exception:
                pass

            if self._right is not self._left:
                try:
                    self._right.display(img.transpose(Image.FLIP_LEFT_RIGHT))
                except Exception:
                    pass

            elapsed = time.monotonic() - start_time
            sleep_duration = frame_time - elapsed
            if sleep_duration > 0:
                time.sleep(sleep_duration)
