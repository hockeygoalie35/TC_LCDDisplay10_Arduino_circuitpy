# Tested on Arduino NanoRP2040 Connect

from machine import I2C, Pin
import time

import LCDDisplay10

# Create an I2C object out of our SDA and SCL pin objects
sda_pin = Pin(12) # GPIO12, A4, D18, STEMMA QT - blue wire (for Arduino NanoRP2040 Connect)
scl_pin = Pin(13) # GPIO13, A5, D19, STEMMA QT - yellow wire (for Arduino NanoRP2040 Connect)
i2c = machine.I2C(id=0, scl=scl_pin, sda=sda_pin, freq=10000)
# i2c = machine.SoftI2C(scl=scl_pin, sda=sda_pin, freq=400_000)
display = LCDDisplay10.LCDDisplay10(i2c)

def setup():
    # print(i2c.scan())
    display.reset()
    display.print_to_lcd("8.8.8.8.8.8.8.8.8.8.")
    display.set_thousands(display.T_1 | display.T_3 | display.T_5 | display.T_7 | display.T_2 | display.T_4 | display.T_6)
    display.set_memory(True)
    display.set_negative(True)
    display.set_error(True)
    display.send_buffer()
    time.sleep_ms(2000)


def loop():
  flag = True
  display.clear()
  time.sleep_ms(1000)
  display.print_to_lcd("1234567890")
  display.set_memory(flag)
  display.set_negative(flag)
  display.set_error(flag)
  if flag:
    display.set_thousands(display.T_1 | display.T_3 | display.T_5 | display.T_7)
  else:
    display.set_thousands(display.T_2 | display.T_4 | display.T_6)
  flag = not flag
  for i in range(10):
    display.set_point_pos(i)
    display.send_buffer()
    time.sleep_ms(1000)

setup()

while(True):
    loop()
    time.sleep_ms(1000)
