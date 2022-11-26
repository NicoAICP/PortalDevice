import board
import digitalio
import os
import ipaddress
import wifi
import time

class con:
    def connect():

        led = digitalio.DigitalInOut(board.LED)
        led.direction = digitalio.Direction.OUTPUT
        led.value = True
        time.sleep(1)
        led.value = False
        wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'))

        
        led.value = True
        time.sleep(1)
        led.value = False
        #print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])

        #print("My IP address is", wifi.radio.ipv4_address)
        led.value = True
        time.sleep(1)
        led.value = False

        ipv4 = ipaddress.ip_address("8.8.4.4")
        wifi.radio.ping(ipv4)
        led.value = True