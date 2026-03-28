import socket
import time

# Use the Broadcast address for your subnet (usually .255)
# This sends the audio to every device on the network.
BROADCAST_IP = "192.168.0.255" 
PORT = 5005
FILENAME = "Travelers.wav"

def stream_audio():
    print(f"Broadcasting {FILENAME} to {BROADCAST_IP}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # This allows the laptop to send packets to the broadcast address
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        with open(FILENAME, "rb") as f:
            f.seek(44) # Skip WAV header
            while True:
                data = f.read(1024)
                if not data:
                    break
                # Send to the broadcast address
                sock.sendto(data, (BROADCAST_IP, PORT))
                
                # Pico W needs a slightly longer breath than a PC
                time.sleep(0.025) 
                
    except FileNotFoundError:
        print(f"Error: {FILENAME} not found in this folder.")
    finally:
        sock.close()
    print("Finished streaming.")

if __name__ == "__main__":
    # Just run once for testing
    stream_audio()
