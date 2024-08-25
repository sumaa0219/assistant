from machine import Pin
import time

led_pin_number = 2
led = Pin(led_pin_number, Pin.OUT)

def off():
    led.value(0)
    
def on():
    led.value(1)
    
def blink(count:int):
    for x in range(count):
        led.value(1)
        time.sleep_ms(200)
        led.value(0)
        time.sleep_ms(200)