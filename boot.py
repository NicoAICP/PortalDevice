import board
import storage
import supervisor
import usb_cdc
import usb_hid
import usb_midi
from digitalio import Pull

import safe_mode
from portal import Portal
from internet import con

safe_mode.enable(board.GP14, Pull.UP)

storage.remount("/", False)

#storage.disable_usb_drive()
usb_cdc.disable()
usb_midi.disable()
con.connect()
supervisor.set_usb_identification(Portal.MANUFACTURER, Portal.PRODUCT, Portal.VID, Portal.PID)

usb_hid.enable((Portal.get_hid_device(),))