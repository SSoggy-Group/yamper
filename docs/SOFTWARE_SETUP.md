# Yamper — Software Setup Guide

Complete step-by-step instructions for setting up Yamper on a fresh Raspberry Pi Zero 2 WH.

No desktop environment, no HDMI, no keyboard required after initial setup.

---

## 1. Flash the SD card

1. Download and install **Raspberry Pi Imager** on your computer.
2. Insert your microSD card (32 GB or larger).
3. Open Raspberry Pi Imager and choose:
   - **Device:** Raspberry Pi Zero 2 W
   - **OS:** Raspberry Pi OS Lite (64-bit)
   - **Storage:** your SD card
4. Click the **gear icon** (⚙️) or "Edit Settings" before writing:
   - ✅ Set hostname: `yamper`
   - ✅ Enable SSH → Use password authentication
   - ✅ Set username: `pi` and a password you'll remember
   - ✅ Configure wireless LAN → enter your WiFi name and password
   - ✅ Set locale and timezone
5. Click **Write** and wait for it to finish.

## 2. First boot

1. Insert the SD card into the Pi and power it on.
2. Wait about 60–90 seconds for the first boot.
3. From your computer, connect via SSH:

```bash
ssh pi@yamper.local
```

> If `yamper.local` doesn't work, find the Pi's IP address in your router's admin page and use `ssh pi@<IP>`.

4. Update the system:

```bash
sudo apt update && sudo apt upgrade -y
```

## 3. Enable I2C (for the OLED eyes)

```bash
sudo raspi-config
```

Navigate to: **Interface Options → I2C → Enable → Finish**

Verify I2C is working:

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

You should see `3c` (and possibly `3d`) in the grid. These are your OLED displays.

## 4. Enable I2S audio (for mic and speaker)

Edit the boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

> **Note:** On older Raspberry Pi OS versions, the file might be at `/boot/config.txt` instead.

Add these lines at the bottom:

```ini
# I2S audio for INMP441 mic and MAX98357A amp
dtoverlay=googlevoicehat-soundcard
```

> **Alternative:** If `googlevoicehat-soundcard` doesn't work, try:
> ```ini
> dtoverlay=hifiberry-dac
> dtoverlay=i2s-mmap
> ```

Save and reboot:

```bash
sudo reboot
```

After reboot, SSH in again and check:

```bash
arecord -l
aplay -l
```

You should see at least one recording device and one playback device.

## 5. Install system dependencies

```bash
sudo apt install -y \
  python3-pip \
  python3-venv \
  python3-dev \
  libopenblas-dev \
  libasound2-dev \
  portaudio19-dev \
  ffmpeg \
  git
```

## 6. Clone the project

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/yamper.git
cd yamper/software
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

## 7. Create a Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

From now on, always activate the venv before running Yamper commands:

```bash
source ~/yamper/software/.venv/bin/activate
```

## 8. Install Python packages

```bash
pip install -r requirements.txt
```

This installs: `openai`, `Pillow`, `luma.oled`, `RPi.GPIO`, `sounddevice`, `numpy`, `python-dotenv`, `pydub`.

> **Note:** On the Pi Zero 2 W this may take 5–10 minutes. Be patient.

## 9. Set up your OpenAI API key

```bash
cp ../.env.example .env
nano .env
```

Replace `sk-your-key-here` with your real OpenAI API key. Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

> Get an API key at https://platform.openai.com/api-keys

## 10. Test the hardware

Run each test one at a time to verify your wiring:

### Test the OLED eyes

```bash
python3 -m mimo.test_eyes
```

You should see different eye animations cycle on the OLED screens.

### Test the button

```bash
python3 -m mimo.test_button
```

Press the button — you should see messages in the terminal. The LED should light up while the button is held. Press `Ctrl+C` to stop.

### Test the microphone

```bash
python3 -m mimo.test_mic
```

Speak during the 3-second recording. It will play back what it heard.

### Test the speaker

```bash
python3 -m mimo.test_speaker
```

You should hear a 440 Hz beep tone.

### Test the OpenAI API

```bash
python3 -m mimo.test_openai
```

You should hear the robot say a greeting.

## 11. Run Yamper manually

Once all tests pass:

```bash
python3 -m mimo.main
```

Press the button, speak, and Yamper will respond!

Press `Ctrl+C` to stop.

## 12. Enable autostart on boot

Copy the systemd service file:

```bash
sudo cp ~/yamper/software/systemd/yamper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable yamper
sudo systemctl start yamper
```

Check that it's running:

```bash
sudo systemctl status yamper
```

View live logs:

```bash
journalctl -u yamper -f
```

Now Yamper will start automatically every time the Pi boots.

### To stop or restart:

```bash
sudo systemctl stop yamper
sudo systemctl restart yamper
```

### To disable autostart:

```bash
sudo systemctl disable yamper
```

---

## Troubleshooting

### "No OLED found"

- Run `i2cdetect -y 1` and check that `3c` or `3d` appears.
- Verify SDA → GPIO 2, SCL → GPIO 3.
- Check VCC is connected to 3.3V.

### "No sound device" or "recording failed"

- Check `arecord -l` and `aplay -l`.
- Make sure the I2S overlay is in `/boot/firmware/config.txt`.
- Reboot after changing config.txt.
- Wiring: BCLK → GPIO 18, LRCLK → GPIO 19, DIN → GPIO 20, DOUT → GPIO 21.

### "OPENAI_API_KEY not set"

- Make sure `software/.env` exists and has a valid key.
- The key must start with `sk-`.

### "WiFi error eyes" (no-wifi symbol on screen)

- Check WiFi: `ping 8.8.8.8`
- Reconnect: `sudo raspi-config` → System Options → Wireless LAN.

### Button not working

- Check wiring: one switch leg to GPIO 17, other to GND.
- The code uses an internal pull-up resistor, so no external resistor is needed.

### MP3 playback fails

- Make sure `ffmpeg` is installed: `sudo apt install ffmpeg`
- The `pydub` package uses `ffmpeg` to decode MP3 files from OpenAI TTS.

### Audio too quiet or too loud

- Use `alsamixer` to adjust volume: `alsamixer`
- Use arrow keys to change levels. Press `Esc` to save.

---

## File layout

```
yamper/
├── .env.example                # copy to software/.env
├── docs/
│   └── SOFTWARE_SETUP.md       # this file
├── software/
│   ├── .env                    # your API key (not in git)
│   ├── requirements.txt        # Python dependencies
│   ├── systemd/
│   │   └── yamper.service      # autostart service
│   └── mimo/
│       ├── __init__.py
│       ├── config.py           # all settings and pin numbers
│       ├── main.py             # main app loop
│       ├── eyes.py             # OLED eye animations
│       ├── button.py           # GPIO button handler
│       ├── audio.py            # mic, speaker, OpenAI API
│       ├── test_eyes.py        # test: OLED displays
│       ├── test_button.py      # test: push button
│       ├── test_mic.py         # test: microphone
│       ├── test_speaker.py     # test: speaker
│       └── test_openai.py      # test: OpenAI API
└── hardware/
    └── ...                     # 3D print files
```
