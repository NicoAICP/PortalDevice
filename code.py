import usb_hid

from logger import Logger
from portal import Portal

logger = Logger('code.py', '/log.txt')
logger.log(Logger.INFO, "running code.py")

portal = Portal(usb_hid.devices)