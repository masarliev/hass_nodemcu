# nodemcu pir, dht and switches

Example home-assistant configuration

```yaml
binary_sensor:
  - platform: mqtt
    state_topic: "home/bedroom/pir"
    payload_on: "on"
    payload_off: "off"
    name: "Motion"
    device_class: motion
switch:
  - platform: mqtt
    name: "Fan"
    command_topic: "home/bedroom/set/fan"
    state_topic: "home/bedroom/fan"
    qos: 1
    retain: true
    payload_on: "on"
    payload_off: "off"

  - platform: mqtt
    name: "Light"
    command_topic: "home/bedroom/set/light"
    state_topic: "home/bedroom/light"
    qos: 1
    retain: true
    payload_on: "on"
    payload_off: "off"
sensor:
  - platform: mqtt
    state_topic: "home/bedroom/temperature"
    name: "Temperature"
    unit_of_measurement: "°C"

  - platform: mqtt
    state_topic: "home/bedroom/humidity"
    name: "Humidity"
    unit_of_measurement: "%"
```
