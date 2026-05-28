# Installation on Raspberry Pi OS

Follow these steps to set up Yamper on a headless Raspberry Pi Zero 2 WH.

## 1. System Setup
1. Flash Raspberry Pi OS Lite (64-bit) onto your SD card.
2. Boot the Pi and connect via SSH.
3. Open the configuration menu:
   ```bash
   sudo raspi-config
   ```
4. Navigate to **Interface Options**:
   - Enable **I2C** (for the OLED screens)
5. Save and reboot.

## 2. Dependencies
Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv portaudio19-dev libasound2-dev ffmpeg
```

## 3. Clone and Setup Python Environment
Clone the repository:
```bash
git clone https://github.com/SSoggy-Group/yamper.git
cd yamper/software
```

Install Python packages:
```bash
# Optional: create a venv if your OS requires it
pip3 install -r requirements.txt
```

## 4. Configuration
Copy the sample config and add your API keys:
```bash
cd yamper/software
cp .env.example .env
nano .env
```
Add your `OPENAI_API_KEY` or `HACKCLUB_API_KEY`.

## 5. Enable Systemd Service
To make Yamper start automatically on boot:

```bash
sudo cp ../systemd/yamper.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable yamper.service
sudo systemctl start yamper.service
```

You can check the logs using:
```bash
sudo journalctl -u yamper.service -f
```
