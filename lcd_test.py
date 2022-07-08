# Tested on Arduino NanoRP2040 Connect


import board
import busio
import time
import LCDDisplay10



# Create an I2C object out of our SDA and SCL pin objects
i2c = board.I2C()
i2c.try_lock()
print([hex(device_address) for device_address in i2c.scan()])


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
    time.sleep(4)
    display.set_blink(display.BLINK_FAST)
    time.sleep(4)
    display.set_blink(display.BLINK_NORMAL)
    time.sleep(4)
    display.set_blink(display.BLINK_SLOW)
    time.sleep(4)
    display.set_blink(display.NO_BLINK)
    time.sleep(4)


def loop():
  flag = True
  display.clear()
  time.sleep(1)
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
    time.sleep(1)
setup()

while(True):
    loop()
    time.sleep(1)
