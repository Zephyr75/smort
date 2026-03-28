import network
import socket
import machine
import array
import time

# --- WIFI SETUP ---
WLAN_SSID = "TP-Link_D035"
WLAN_PASS = "55990691"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WLAN_SSID, WLAN_PASS)

print("Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)
print("Connected! Pico IP:", wlan.ifconfig()[0])

# --- I2S SETUP ---
# Increased ibuf to handle network jitters
audio_out = machine.I2S(0, sck=machine.Pin(9), ws=machine.Pin(10), sd=machine.Pin(11),
                        mode=machine.I2S.TX, bits=16, format=machine.I2S.MONO, 
                        rate=16000, ibuf=20480)

# --- STREAMING LOGIC ---
def start_receiver(volume=0.25):
    # Bind to '0.0.0.0' to catch Broadcast packets
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', 5005))
    
    # Important for MicroPython: allow the socket to be reused immediately
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    print("Waiting for audio stream on port 5005...")
    
    while True:
        try:
            # Pico W buffer can handle 2048, but 1024 is safer
            data, addr = sock.recvfrom(2048)
            
            # Debug: Print only every 50th packet so we don't lag the audio
            # But for the FIRST packet, we definitely want to see it
            if data:
                # Convert to 16-bit integers
                samples = array.array('h', data)
                
                # Apply Volume scaling
                for i in range(len(samples)):
                    samples[i] = int(samples[i] * volume)
                
                # Write to I2S
                audio_out.write(samples)
                
        except Exception as e:
            print(f"Error during playback: {e}")
            break

try:
    start_receiver(volume=0.25)
except KeyboardInterrupt:
    print("Stopping...")
    audio_out.deinit()
