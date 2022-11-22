import board
import storage
import supervisor
import usb_cdc
import usb_hid
import usb_midi
from digitalio import Pull

import safe_mode
from logger import Logger
from portal import Portal

safe_mode.enable(board.GP14, Pull.UP)

storage.remount("/", False)

logger = Logger('boot.py', '/log.txt')
logger.log(Logger.INFO, "running boot.py")

storage.disable_usb_drive()
usb_cdc.disable()
usb_midi.disable()

supervisor.set_usb_identification(Portal.MANUFACTURER, Portal.PRODUCT, Portal.VID, Portal.PID)

usb_hid.enable((Portal.get_hid_device(),))