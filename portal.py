try:
    from typing import Sequence
except ImportError:
    pass

import asyncio
import binascii
import usb_hid

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
        self.portal_hid = self.__find_device(devices)
        self.status_index = 0x00
        self.is_active = 0x00
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

    async def __handle_incoming_report(self, report_in: bytes):
        if (report_in[0] == ord('A')):
            await self.__activate(report_in)
        elif (report_in[0] == ord('C')): # ignore
            pass # ignore color request
        elif (report_in[0] == ord('J')): # ignore
            pass # ignore sound request
        elif (report_in[0] == ord('L')): # ignore
            pass # ignore light (Trap slot)
        elif (report_in[0] == ord('M')): # ignore
            pass # ignore speaker request -> ignore")
        elif (report_in[0] == ord('Q')):
            await self.__query(report_in)
        elif (report_in[0] == ord('R')):
            await self.__reset(report_in)
        elif (report_in[0] == ord('S')):
            await self.__status(report_in)
        elif (report_in[0] == ord('W')):
            await self.__write(report_in)
        else:
            pass

    async def __reset(self, report_in: bytes):
        report_out = bytearray(self.REPORT_LENGTH)
        report_out[0] = ord('R') # 0x52
        report_out[1] = 0x02
        report_out[2] = 0x18
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    async def __status(self, report_in: bytes):
        report_out = bytearray(self.REPORT_LENGTH)
        report_out[0] = ord('S') # 0x53
        report_out[1] = 0x03
        report_out[2] = 0x00
        report_out[3] = 0x00
        report_out[4] = 0x00
        report_out[5] = self.status_index
        report_out[6] = self.is_active
        self.status_index += 1
        self.status_index %= 0xFF
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    async def __activate(self, report_in: bytes):
        self.is_active = report_in[1]
        report_out = bytearray(self.REPORT_LENGTH)
        report_out[0] = ord('A') # 0x41
        report_out[1] = report_in[1]
        report_out[2] = 0xFF
        report_out[3] = 0x77
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    async def __query(self, report_in: bytes):
        slot = report_in[1] % 0x10 + 1
        block = report_in[2]
        report_out = bytearray(self.REPORT_LENGTH)
        report_out[0] = ord('Q') # 0x51
        report_out[1] = report_in[1] # character slot
        report_out[2] = report_in[2] # data block index
        # TODO: append 16 bytes of requested data block here
        #report_out[3:19] = data
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    async def __write(self, report_in: bytes):
        slot = report_in[1] % 0x10 + 1
        block = report_in[2]
        data = report_in[3:19]
        # TODO: write new data block
        report_out = bytearray(self.REPORT_LENGTH)
        report_out[0] = ord('W') # 0x57
        report_out[1] = report_in[1] # character slot
        report_out[2] = report_in[2] # data block index
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    async def __worker(self):
        report_task = asyncio.create_task(self.__get_last_received_report())
        await asyncio.gather(report_task)       

    async def __get_last_received_report(self):
        while True:
            report_in = self.portal_hid.get_last_received_report()
            if (report_in != None):
                await self.__handle_incoming_report(report_in)
            await asyncio.sleep(0)

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

