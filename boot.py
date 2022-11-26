import board
import storage
import supervisor
import usb_cdc
import usb_hid
import usb_midi
from digitalio import Pull

import board
import digitalio

import safe_mode
from portal import Portal

import os
import wifi
import time

safe_mode.enable(board.GP14, Pull.UP)

storage.remount("/", False)

#storage.disable_usb_drive()
#usb_cdc.disable()
usb_midi.disable()

supervisor.set_usb_identification(Portal.MANUFACTURER, Portal.PRODUCT, Portal.VID, Portal.PID)

usb_hid.enable((Portal.get_hid_device(),))

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
while (wifi.radio.ipv4_address == None):
    print("trying to connect...")
    try:
        led.value = True
        led.value = False
        
        wifi.radio.connect(os.getenv('WIFI_SSID'), os.getenv('WIFI_PASSWORD'),timeout=5)
    except:
        print("failed to connect...")

print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("My IP address is", wifi.radio.ipv4_address)