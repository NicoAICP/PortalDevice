import usb_hid

from portal import Portal

#Needed for WIFI, placed in code.py since it locks up everything else otherwise
import socketpool
import wifi
from adafruit_httpserver.server import HTTPServer
from adafruit_httpserver.response import HTTPResponse



pool = socketpool.SocketPool(wifi.radio)
server = HTTPServer(pool)
        

@server.route("/")
def base(request): # pylint: disable=unused-arguments
    """Return the current temperature"""
    # pylint: disable=no-member
    print("in request")
    return HTTPResponse(body="Hello World")


portal = Portal(usb_hid.devices)
server.start(str(wifi.radio.ipv4_address))
while True:
    try:
        portal.process_reports()
        server.poll()     
    except:
        continue