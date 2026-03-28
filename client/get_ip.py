import network
import time

# --- EDIT THESE ---
SSID = "TP-Link_D035"
PASSWORD = "55990691"

def connect_and_get_ip():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print(f"Connecting to {SSID}...")
        wlan.connect(SSID, PASSWORD)
        
        # Wait up to 10 seconds for connection
        timeout = 10
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            
    if wlan.isconnected():
        # ifconfig() returns (IP, Subnet, Gateway, DNS)
        ip_info = wlan.ifconfig()
        print("-" * 30)
        print(f"CONNECTED!")
        print(f"Pico IP Address: {ip_info[0]}")
        print("-" * 30)
    else:
        print("FAILED: Could not connect to WiFi. Check your SSID/Password.")

if __name__ == "__main__":
    connect_and_get_ip()
