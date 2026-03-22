import machine
from pico_i2c_lcd import I2cLcd
import time

# 1. I2C Configuration
I2C_ADDR = 0x27
i2c = machine.I2C(0, sda=machine.Pin(0), scl=machine.Pin(1), freq=400000)
lcd = I2cLcd(i2c, I2C_ADDR, 4, 20)

# 2. Backlight PWM Configuration (GP3)
backlight = machine.PWM(machine.Pin(3))
backlight.freq(1000)

def set_brightness(percentage):
    # Duty cycle is 0 to 65535
    duty = int((percentage / 100) * 65535)
    backlight.duty_u16(duty)

# 3. Define Custom Characters
lcd.custom_char(0, bytearray([0x02,0x03,0x02,0x0E,0x1E,0x0C,0x00,0x00])) # ♪
lcd.custom_char(1, bytearray([0x10,0x18,0x1C,0x1E,0x1C,0x18,0x10,0x00])) # ▶
lcd.custom_char(2, bytearray([0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x1B,0x00])) # ▐▐
lcd.custom_char(3, bytearray([0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F,0x1F])) # █

def show_player():
    # Set brightness to 50% before showing UI
    set_brightness(30)
    
    lcd.clear()
    
    # Line 1: ♪ Blinding Bobs
    lcd.move_to(0, 0)
    lcd.putchar(chr(0))
    lcd.putstr(" Blinding Bobs")
    
    # Line 2: The Weeknd + Play Icon
    lcd.move_to(2, 1)
    lcd.putstr("The Weeknd")
    lcd.move_to(18, 1)
    lcd.putchar(chr(1))
    
    # Line 3: Progress Bar
    lcd.move_to(0, 2)
    lcd.putstr("[")
    for _ in range(8): lcd.putchar(chr(3))
    lcd.putstr("....] 2:14")
    
    # Line 4: Controls
    lcd.move_to(0, 3)
    lcd.putstr("|<<  ")
    lcd.putchar(chr(2))
    lcd.putstr("   >  >> ")
    lcd.putchar(chr(0))

if __name__ == "__main__":
    show_player()
