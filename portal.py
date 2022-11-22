try:
    from typing import Sequence
except ImportError:
    pass

import asyncio
import binascii
import usb_hid

from logger import Logger


class Portal:
    """Emulates Portal of Power
    """

    MANUFACTURER = "Activision"
    PRODUCT = "Spyro Porta"
    VID = 0x1430
    PID = 0x0150

    USAGE_PAGE = 0xFF00
    USAGE = 0x01
    REPORT_ID = 0
    REPORT_LENGTH = 32

    PORTAL_REPORT_DESCRIPTOR = bytes((
        0x06, 0x00, 0xFF,  # Usage Page (Vendor Defined 0xFF00)
        0x09, 0x01,        # Usage (0x01)
        0xA1, 0x01,        # Collection (Application)
        0x19, 0x01,        #   Usage Minimum (0x01)
        0x29, 0x40,        #   Usage Maximum (0x40)
        0x15, 0x00,        #   Logical Minimum (0)
        0x26, 0xFF, 0x00,  #   Logical Maximum (255)
        0x75, 0x08,        #   Report Size (8)
        0x95, 0x20,        #   Report Count (32)
        0x81, 0x00,        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
        0x19, 0x01,        #   Usage Minimum (0x01)
        0x29, 0x40,        #   Usage Maximum (0x40)
        0x91, 0x00,        #   Output (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
        0xC0,              # End Collection
    ))

    def __init__(self, devices: Sequence[usb_hid.Device]) -> None:
        """Create a Portal object that will send and receive HID reports.
        """
        self.logger = Logger('portal.py', '/log.txt')
        self.logger.log(Logger.DEBUG, "__init__")
        
        self.portal_hid = self.__find_device(devices)
        self.logger.log(Logger.DEBUG, str(self.portal_hid))

        asyncio.run(self.__worker())

    def __find_device(self, devices: Sequence[usb_hid.Device]) -> usb_hid.Device:
        """Search through the provided sequence of devices to find the USB HID Portal device.
        """
        if hasattr(devices, "send_report"):
            devices = [devices]  # type: ignore
        for device in devices:
            if (device.usage_page == self.USAGE_PAGE and device.usage == self.USAGE and hasattr(device, "send_report")):
                return device
        raise ValueError("Could not find matching HID device.")

    async def __worker(self):
        self.logger.log(Logger.DEBUG, "worker starting")
        report_task = asyncio.create_task(self.__get_last_received_report())
        await asyncio.gather(report_task)
        self.logger.log(Logger.DEBUG, "worker done")

    async def __get_last_received_report(self):
        while True:
            report_in = self.portal_hid.get_last_received_report()
            if (report_in != None):
                self.logger.log(Logger.DEBUG, binascii.hexlify(report_in).decode('ascii'))
                await asyncio.sleep(1)

    @staticmethod
    def get_hid_device() -> usb_hid.Device:
        """Create a USB HID Portal device
        """
        return usb_hid.Device(
            report_descriptor = Portal.PORTAL_REPORT_DESCRIPTOR,
            usage_page = Portal.USAGE_PAGE,               # Generic Desktop Control                     ## Must match Usage Page above!
            usage = Portal.USAGE,                         # Portal                                      ## Must match Usage above!
            report_ids = (Portal.REPORT_ID,),             # Descriptor uses report ID 0.                ## Must match Report ID above!
            in_report_lengths = (Portal.REPORT_LENGTH,),  # The portal sends 32 bytes in its report.    ## Must match number of bytes above! (Report Size * Report Count)
            out_report_lengths = (Portal.REPORT_LENGTH,), # The portal receives 32 bytes in its report. ## Must match number of bytes above! (Report Size * Report Count)
        )

