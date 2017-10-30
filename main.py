import network
import machine
from hass import Hass

# setup internet connection
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wlan.connect('SSID', 'password')
    while not wlan.isconnected():
        pass

# setup sensors and switches
SENSORS = [
    {'name': 'dht',   'pin': machine.Pin(5)},
    {'name': 'pir',   'pin': machine.Pin(4, machine.Pin.IN)},
    {'name': 'light', 'pin': machine.Pin(0, machine.Pin.OUT, value=0)},
    {'name': 'fan',   'pin': machine.Pin(2, machine.Pin.OUT, value=0)}
]
# initialize service
service = Hass('bedroom', SENSORS)
service.BROKER_PASS = '1234'  # set configuration
service.listen()
