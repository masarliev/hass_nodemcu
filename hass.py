from umqtt.simple import MQTTClient
import utime
import ure
import machine
import dht


class Hass(object):
    DELAY = 20
    BROKER_HOST = '192.168.0.1'
    BROKER_USER = 'homeassistant'
    BROKER_PASS = 'password'

    def __init__(self, room, sensors):
        self.room = room
        self.client = MQTTClient(self.room, self.BROKER_HOST, 1883,
                                 self.BROKER_USER, self.BROKER_PASS)
        self.client.set_callback(self.mqtt_callback)
        self._connect()
        self._sensors = []
        for item in sensors:
            if item['name'] == 'dht':
                item['pin'] = dht.DHT11(item['pin'])
            if hasattr(item['pin'], 'irq'):
                item['pin'].irq(
                    trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING,
                    handler=self._partial(self.set_state, switch=item['name'])
                )
            self._sensors.append(item)
        self._states = {}

    def set_state(self, msg, switch):
        if isinstance(msg, (machine.Pin,)):
            payload = 'on' if msg.value() == 1 else 'off'
        else:
            payload = str(msg)
        self._states[switch] = payload
        self._send('home/%s/%s' % (self.room, switch), payload)

    def mqtt_callback(self, topic, message):
        search = ure.search('home/%s/set/(\w+)' % self.room, topic)
        try:
            generator = (x['pin'] for x in self._sensors
                         if x['name'] == search.group(1).decode("utf-8"))
            pin = next(generator)
            getattr(pin, message.decode("utf-8").lower())()
        except (KeyError, AttributeError, StopIteration):
            pass

    def dht_callback(self, timer, sensor):
        sensor.measure()
        if ('temperature' not in self._states or
                self._states['temperature'] != str(sensor.temperature())):
            self.set_state(sensor.temperature(), 'temperature')
        if ('humidity' not in self._states or
                self._states['humidity'] != str(sensor.humidity())):
            self.set_state(sensor.humidity(), 'humidity')

    def _connect(self):
        self._isconnected = False
        while not self._isconnected:
            try:
                self._states = {}  # clear states if disconnected
                self.client.connect()
                self.client.subscribe("home/%s/set#" % self.room, 1)
                self._isconnected = True
            except OSError:
                utime.sleep(self.DELAY)

    def _partial(self, func, *args, **kwargs):
        def _func(*more_args, **more_kwargs):
            kw = kwargs.copy()
            kw.update(more_kwargs)
            return func(*(args + more_args), **kw)
        return _func

    def _send(self, topic, message):
        try:
            self.client.publish(topic, message, qos=1)
        except OSError:
            self._connect()

    def listen(self):
        try:
            dht_sensor = next(
                x['pin'] for x in self._sensors if x['name'] == 'dht')
            tim = machine.Timer(-1)
            tim.init(period=5000, mode=machine.Timer.PERIODIC,
                     callback=self._partial(
                         self.dht_callback, sensor=dht_sensor))
        except StopIteration:
            pass
        while True:
            try:
                self.client.wait_msg()
            except OSError:
                self._connect()
