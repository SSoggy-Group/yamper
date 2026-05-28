import time
from . import config
from . import wifi
from . import wifi_portal

def run_setup_mode(eyes):
    print("entering wifi setup mode...")
    
    # 1. Update display to setup state
    eyes.set_state("wifi_setup")
    
    error_msg = None
    
    while True:
        wifi.set_setup_status("scanning...")
        print("scanning for networks...")
        networks = wifi.scan_networks()

        # 2. Start Hotspot
        wifi.set_setup_status("hotspot starting")
        if not wifi.start_hotspot():
            print("Failed to start hotspot! Retrying in 10s...")
            time.sleep(10)
            continue
            
        wifi.set_setup_status("portal ready")
        print(f"Hotspot started. Connect to '{config.WIFI_SETUP_AP_SSID}'.")
        
        # 3. Run Portal
        ssid = None
        password = None
        try:
            # Blocks until credentials are submitted
            ssid, password = wifi_portal.run_portal(config.WIFI_SETUP_PORT, error_msg=error_msg, networks=networks)
        except Exception:
            # Password safety: never print raw exceptions that could contain passwords
            print("Portal encountered an error.")
            
        # 4. Stop Hotspot before trying to connect
        wifi.set_setup_status("connecting")
        print("stopping hotspot...")
        wifi.stop_hotspot()
        
        # Give wireless interface a moment to settle
        time.sleep(2)
        
        if not ssid:
            wifi.set_setup_status("failed")
            error_msg = "No network selected."
            continue
            
        # 5. Connect to chosen WiFi
        print(f"Connecting to SSID '{ssid}'...")
        success = wifi.connect_to_wifi(ssid, password)
        
        if success:
            wifi.set_setup_status("success")
            print("Connected successfully!")
            return True
        else:
            wifi.set_setup_status("failed")
            print("Connection failed.")
            error_msg = "Failed to connect. Please check password and try again."
            # Wait a few seconds before restarting the hotspot
            time.sleep(3)
