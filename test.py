''' from machine import Pin
from time import sleep

relay = Pin(14, Pin.OUT)  # Change 15 to match your GPIO pin

while True:
    print("Relay ON")
    relay.high()  # Send 3.3V
    sleep(6)

    print("Relay OFF")
    relay.low()   # Send 0V
    sleep(6) '''

# Only used for testing the MOSFET/Relay module using logic-level.