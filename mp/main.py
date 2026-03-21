import machine
from pico_i2c_lcd import I2cLcd
import time

# I2C Configuration
I2C_ADDR = 0x27  # Common address for Freenove/I2C LCDs
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)

# Define Custom Characters (8 max)
# 0: Eighth Note, 1: Play Arrow, 2: Pause Bars, 3: Full Block
lcd.custom_char(0, bytearray([0x02,0x03,0x02,0x0E,0x1E,0x0C,0x00,0x00])) # ♪
lcd.custom_char(1, bytearray([0x10,0x18,0x1C,0x1E,0x1C,0x18,0x10,0x00])) # ▶
lcd.custom_char(2, bytearray([0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x00])) # ▐▐
lcd.custom_char(3, bytearray([0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])) # █

def show_player():
    lcd.clear()
    
    # Line 1: ♪ Blinding Lights
    lcd.move_to(0, 0)
    lcd.putchar(chr(0)) # Custom ♪
    lcd.putstr(" Blinding Lights")
    
    # Line 2: The Weeknd + Play Icon
    lcd.move_to(2, 1)
    lcd.putstr("The Weeknd")
    lcd.move_to(18, 1)
    lcd.putchar(chr(1)) # Custom ▶
    
    # Line 3: Progress Bar [████████░░░░] 2:14
    lcd.move_to(0, 2)
    lcd.putstr("[")
    for _ in range(8): lcd.putchar(chr(3)) # 8 Full Blocks
    lcd.putstr("....] 2:14") # Using '.' for empty for now
    
    # Line 4: Controls |◄◄  ▐▐   ►  ►► ♫
    lcd.move_to(0, 3)
    lcd.putstr("|<<  ")
    lcd.putchar(chr(2)) # Custom ▐▐
    lcd.putstr("   >  >> ")
    lcd.putchar(chr(0)) # Another ♪

if __name__ == "__main__":
    show_player()
