import machine
import math
import struct
import time

# 1. Setup I2S Pins
bck_pin = machine.Pin(9)   # Bit Clock (BCLK)
ws_pin = machine.Pin(10)   # Word Select / LRCLK (LRC)
sdout_pin = machine.Pin(11) # Data Out (DIN)

# 2. Initialize the I2S Audio Bus
audio_out = machine.I2S(
    0, 
    sck=bck_pin, 
    ws=ws_pin, 
    sd=sdout_pin, 
    mode=machine.I2S.TX, 
    bits=16, 
    format=machine.I2S.MONO, 
    rate=16000, 
    ibuf=20000 # Increased buffer size for stability
)

notes = {
    "Do": 261.63, "Re": 293.66, "Mi": 329.63,
    "Fa": 349.23, "Sol": 392.00, "La": 440.00, "Si": 493.88
}

def play_tone(frequency, duration_ms, volume=0.05):
    """Pre-calculates a flawless sine wave buffer and plays it."""
    sample_rate = 16000
    # Calculate exact number of samples needed for the duration
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    
    # Allocate a byte array (16-bit audio = 2 bytes per sample)
    # The Pico has plenty of RAM to hold a 400ms note at once.
    buf = bytearray(num_samples * 2) 
    max_amp = 32767 * volume 
    
    # Pre-render the entire note
    for i in range(num_samples):
        t = i / sample_rate
        sample = int(max_amp * math.sin(2 * math.pi * frequency * t))
        
        # --- THE ENVELOPE (FADE IN / FADE OUT) ---
        # This prevents the speaker from "popping" at the start and end
        fade_length = 400 # about 25ms of fading
        if i < fade_length:
            sample = int(sample * (i / fade_length))
        elif i > (num_samples - fade_length):
            sample = int(sample * ((num_samples - i) / fade_length))
            
        # Pack into buffer
        struct.pack_into('<h', buf, i * 2, sample)
        
    # Push the perfectly rendered buffer to the amplifier
    audio_out.write(buf)

# --- Start the Sequence ---
print("Waking up the speaker...")

for note_name, freq in notes.items():
    print(f"Playing: {note_name} ({freq} Hz)")
    play_tone(freq, 400, volume=0.2) 
    time.sleep(0.02) # Tiny breath between notes

# Stop the I2S bus cleanly
time.sleep(0.1)
audio_out.deinit()
print("Sequence Complete.")
