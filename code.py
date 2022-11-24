import usb_hid

from portal import Portal

portal = Portal(usb_hid.devices)

while True:
    try:
        portal.process_reports()
    except:
        continue