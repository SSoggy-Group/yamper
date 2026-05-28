import subprocess
import sys
from . import config

def is_mac():
    return sys.platform == "darwin"

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
    if is_mac():
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
    if is_mac():
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
    except Exception as e:
        print("start_hotspot failed:", e)
        return False

def stop_hotspot():
    if is_mac():
        print("[MOCK] Stopping hotspot")
        return True
    
    try:
        subprocess.run(["nmcli", "connection", "down", "yamper-hotspot"], capture_output=True)
        subprocess.run(["nmcli", "connection", "delete", "yamper-hotspot"], capture_output=True)
        return True
    except Exception as e:
        print("stop_hotspot failed:", e)
        return False

def connect_to_wifi(ssid, password):
    if is_mac():
        print(f"[MOCK] Connecting to '{ssid}'")
        import time
        time.sleep(2)
        return ssid != "Fake_WiFi_2"  # fake failure case
    
    try:
        cmd = ["nmcli", "device", "wifi", "connect", ssid]
        if password:
            cmd.extend(["password", password])
        subprocess.run(cmd, capture_output=True, check=True, timeout=config.WIFI_CONNECT_TIMEOUT)
        return True
    except Exception as e:
        print(f"connect_to_wifi failed for '{ssid}':", e)
        return False
