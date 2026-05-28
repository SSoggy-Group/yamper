import subprocess
import sys
from . import config

_setup_status = "hotspot starting"

def is_mock():
    return sys.platform == "darwin" or getattr(config, "WIFI_MOCK_MODE", False)

def get_setup_status():
    return _setup_status

def set_setup_status(status):
    global _setup_status
    _setup_status = status
    print(f"Status: {status}")

def get_ip_address(ifname="wlan0"):
    if is_mock():
        return "127.0.0.1"
    try:
        import socket
        import fcntl
        import struct
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except Exception:
        try:
            res = subprocess.run(["ip", "-o", "-4", "addr", "show", ifname], capture_output=True, text=True, check=True)
            for line in res.stdout.split("\n"):
                parts = line.split()
                if len(parts) >= 4 and parts[2] == "inet":
                    return parts[3].split("/")[0]
        except Exception:
            pass
        return None

def get_setup_ip():
    ip = get_ip_address("wlan0")
    if ip:
        return ip
    return config.WIFI_SETUP_IP

def internet_ok():
    try:
        subprocess.run(
            ["ping", "-c", "1", "-W", str(config.WIFI_CHECK_TIMEOUT), config.WIFI_CHECK_HOST],
            capture_output=True, check=True
        )
        return True
    except Exception:
        return False

def scan_networks():
    if is_mock():
        return ["Fake_WiFi_1", "Fake_WiFi_2", "My_Home_Network"]
    try:
        res = subprocess.run(
            ["nmcli", "-t", "-f", "SSID", "dev", "wifi"], 
            capture_output=True, text=True, check=True
        )
        # Filter empty and duplicates
        ssids = {s for s in res.stdout.split("\n") if s.strip()}
        return list(ssids)
    except Exception as e:
        print("scan_networks failed:", e)
        return []

def start_hotspot():
    ssid = config.WIFI_SETUP_AP_SSID
    password = config.WIFI_SETUP_AP_PASSWORD
    if is_mock():
        print(f"[MOCK] Starting hotspot '{ssid}'")
        return True
    
    # Check if connection exists, delete it first to be clean
    try:
        subprocess.run(["nmcli", "connection", "delete", "yamper-hotspot"], capture_output=True)
    except Exception:
        pass
        
    cmd = [
        "nmcli", "device", "wifi", "hotspot", 
        "ifname", "wlan0", 
        "ssid", ssid, 
        "con-name", "yamper-hotspot"
    ]
    if len(password) > 0:
        cmd.extend(["password", password])
        
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except Exception:
        print("start_hotspot failed")
        return False

def stop_hotspot():
    if is_mock():
        print("[MOCK] Stopping hotspot")
        return True
    
    try:
        subprocess.run(["nmcli", "connection", "down", "yamper-hotspot"], capture_output=True)
        subprocess.run(["nmcli", "connection", "delete", "yamper-hotspot"], capture_output=True)
        return True
    except Exception:
        print("stop_hotspot failed")
        return False

def connect_to_wifi(ssid, password):
    if is_mock():
        print(f"[MOCK] Connecting to '{ssid}'")
        import time
        time.sleep(2)
        return ssid != "Fake_WiFi_2"  # Fake failure case
    
    try:
        cmd = ["nmcli", "device", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
        # Do not print exception or raw command output to avoid exposing WiFi password in logs
        subprocess.run(cmd, capture_output=True, check=True, timeout=config.WIFI_CONNECT_TIMEOUT)
        return True
    except Exception:
        print(f"connect_to_wifi failed for '{ssid}'")
        return False
