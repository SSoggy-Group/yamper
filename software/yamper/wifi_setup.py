import time
from . import config
from . import wifi
from . import wifi_portal

def run_setup_mode(eyes):
    print("entering wifi setup mode...")
    
    # 1. Update display to setup state
    eyes.set_state("wifi_setup")
    
    # 2. Start Hotspot
    if not wifi.start_hotspot():
        print("Failed to start hotspot! Will retry in 10s...")
        time.sleep(10)
        return False
        
    print(f"Hotspot started. Connect to '{config.WIFI_SETUP_AP_SSID}'.")
    
    # 3. Run Portal
    try:
        # Blocks until setup_success is True in the portal
        wifi_portal.run_portal(config.WIFI_SETUP_PORT)
    except Exception as e:
        print("Portal crashed:", e)
    finally:
        # 4. Stop Hotspot
        print("stopping hotspot...")
        wifi.stop_hotspot()
        
    return True
