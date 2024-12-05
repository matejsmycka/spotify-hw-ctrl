from machine import ADC, Pin, SoftI2C
from pico_i2c_lcd import I2cLcd
import time
import sys, select

i2c = SoftI2C(sda=Pin(27), scl=Pin(26), freq=40000)
lcd = I2cLcd(i2c, 0x3F, 2, 16)
pot = ADC(Pin(28))
button = Pin(29, Pin.IN, Pin.PULL_UP)

button_state = 1
pot_value = 0
user_input = ""
last_input_check = 0


def button_press(pin):
    global button_state
    button_state = pin.value()


def read_pot():
    global pot_value
    pot_value = int(round(pot.read_u16() / 600))
    if pot_value > 100:
        pot_value = 100
    if pot_value < 10:
        pot_value = 0


def display():
    lcd.move_to(0, 1)
    lcd.putstr(
        f"b: {button_state} p:{pot_value}   "
    )  # Ensure spaces to clear residual text
    lcd.move_to(0, 0)
    lcd.putstr(user_input[:16])  # Display the user input (first 16 chars)
    print(f"p={pot_value}")
    print(f"b={button_state}")


def check_user_input():
    global user_input
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        i = input("")
        if len(i) > 1 and i[0] == "$":
            user_input = i[1:]


def main():
    global last_input_check
    while True:
        read_pot()
        display()

        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, last_input_check) >= 1000:
            check_user_input()
            last_input_check = current_time
        time.sleep(1)


button.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=button_press)

main()
