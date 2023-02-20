try:
    from typing import Sequence
except ImportError:
    pass

import os
import struct

import usb_hid

class Toy:
    """Toy used per Slot in the Portal
    """

    def __init__(self, path: str):
        self.needs_saving = False
        self.path = path
        with open(self.path, 'rb') as fp:
            self.data = fp.read()

    def read_block(self, index: int):
        offset = index * 0x10
        length = offset + 0x10
        return self.data[offset:length]

    def write_block(self, index: int, block: bytes):
        offset = index * 0x10
        length = offset + len(block)
        self.data = self.data[0:offset] + block + self.data[length:]

    def save(self):
        with open(self.path, 'wb') as fp:
            fp.write(self.data)

class Slot:
    """Slots used by Portal
    """

    STATUS_EMPTY = 0
    STATUS_PRESENT = 1
    STATUS_REMOVED = 2
    STATUS_ADDED = 3

    def __init__(self):
        self.toy = None
        self.status = Slot.STATUS_EMPTY


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

    MAX_TOYS = 6
    DEFAULT_TOY_PATH = "/toy_{}.dump"

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
        self.__init_slots()

    def __find_device(self, devices: Sequence[usb_hid.Device]) -> usb_hid.Device:
        """Search through the provided sequence of devices to find the USB HID Portal device.
        """
        if hasattr(devices, "send_report"):
            devices = [devices]  # type: ignore
        for device in devices:
            if (device.usage_page == self.USAGE_PAGE and device.usage == self.USAGE and hasattr(device, "send_report")):
                return device
        raise ValueError("Could not find matching HID device.")

    def process_reports(self):
        report_in = self.portal_hid.get_last_received_report()
        if (report_in != None):
            self.__handle_incoming_report(report_in)
            self.__save_toys()

    def update_slot(self, index: int, status: int):
        if (status == Slot.STATUS_ADDED):
            toy_path = self.DEFAULT_TOY_PATH.format(index + 1)
            if (Portal.file_exists(toy_path)):
                self.slots[index].toy = Toy(toy_path)
                self.slots[index].status = Slot.STATUS_ADDED
            else:
                self.slots[index].toy = None
                self.slots[index].status = Slot.STATUS_EMPTY
        elif (status == Slot.STATUS_REMOVED):
            self.slots[index].toy = None
            self.slots[index].status = Slot.STATUS_REMOVED
        elif (status == Slot.STATUS_PRESENT):
            self.slots[index].status = Slot.STATUS_PRESENT

    def __handle_incoming_report(self, report_in: bytes):
        if (report_in[0] == ord('A')):
            self.__activate(report_in)
        elif (report_in[0] == ord('C')): # ignore
            pass # ignore color request
        elif (report_in[0] == ord('J')): # ignore
            pass # ignore sound request
        elif (report_in[0] == ord('L')): # ignore
            pass # ignore light (Trap slot)
        elif (report_in[0] == ord('M')): # ignore
            pass # ignore speaker request -> ignore")
        elif (report_in[0] == ord('Q')):
            self.__query(report_in)
        elif (report_in[0] == ord('R')):
            self.__reset()
        elif (report_in[0] == ord('S')):
            self.__status()
        elif (report_in[0] == ord('W')):
            self.__write(report_in)
        else:
            pass

    def __reset(self):
        self.status_index = 0x00
        report_out = struct.pack('>bH29x', ord('R'), 0x0218)
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    def __status(self):
        slot_status = 0x00000000
        for index in range(self.MAX_TOYS):
            slot_status ^= self.slots[index].status << 2 * (index)
        report_out = struct.pack('<bIbb25x', ord('S'), slot_status, self.status_index, self.is_active)
        self.portal_hid.send_report(report_out, self.REPORT_ID)
        self.status_index += 1
        self.status_index %= 0xFF

    def __activate(self, report_in: bytes):
        self.is_active = report_in[1]
        report_out = struct.pack('>bbH28x', ord('A'), report_in[1], 0xFF77)
        self.portal_hid.send_report(report_out, self.REPORT_ID)
        #self.__status() # proactively send status

    def __query(self, report_in: bytes):
        slot = report_in[1] % 0x10
        block = report_in[2]
        data = self.slots[slot].toy.read_block(block)
        report_out = struct.pack('>b2s16s13x', ord('Q'), report_in[1:3], data)
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    def __write(self, report_in: bytes):
        slot = report_in[1] % 0x10
        block = report_in[2]
        data = report_in[3:19]
        self.slots[slot].toy.write_block(block, data)
        self.slots[slot].toy.needs_saving = True
        report_out = struct.pack('>b2s29x', ord('W'), report_in[1:3])
        self.portal_hid.send_report(report_out, self.REPORT_ID)

    def __init_slots(self):
        self.slots = []
        for index in range(self.MAX_TOYS):
            self.slots.append(Slot())
            self.update_slot(index, Slot.STATUS_ADDED)

    def __save_toys(self):
        for index in range(self.MAX_TOYS):
            if (self.slots[index].toy.needs_saving):
                self.slots[index].toy.save()
                self.slots[index].toy.needs_saving = False

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

    @staticmethod
    def file_exists(path: str) -> bool:
        try:
            os.stat(path)
            return True
        except:
            return False