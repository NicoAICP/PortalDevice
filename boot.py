import supervisor
import usb_hid
import usb_cdc
import usb_midi

usb_cdc.disable()
usb_midi.disable()

supervisor.set_usb_identification("Activision", "Spyro Porta", int(0x1430), int(0x0150))

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
  0x29, 0xFF,        #   Usage Maximum (0x40)
  0x91, 0x00,        #   Output (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
  0xC0,              # End Collection
))

portal = usb_hid.Device(
    report_descriptor=PORTAL_REPORT_DESCRIPTOR,
    usage_page=0xFF00,         # Generic Desktop Control                     ## Must match Usage Page above!
    usage=0x01,                # Portal                                      ## Must match Usage above!
    report_ids=(0,),           # Descriptor uses report ID 0.                ## Must match Report ID above!
    in_report_lengths=(32,),   # The portal sends 32 bytes in its report.    ## Must match number of bytes above! (Report Size * Report Count)
    out_report_lengths=(32,),  # The portal receives 32 bytes in its report. ## Must match number of bytes above! (Report Size * Report Count)
)

usb_hid.enable((portal,))