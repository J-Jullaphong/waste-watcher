import network
import json
from time import sleep
from machine import Pin
from hcsr04 import HCSR04
from umqtt.robust import MQTTClient
from config import (
    WIFI_SSID, WIFI_PASS,
    MQTT_BROKER, MQTT_USER, MQTT_PASS,
    BIN_ID, BIN_CAPACITY
)

led_wifi = Pin(2, Pin.OUT)
led_wifi.value(1)
led_iot = Pin(12, Pin.OUT)
led_iot.value(1)

sensor = HCSR04(trigger_pin=19, echo_pin=18)

wlan = network.WLAN(network.STA_IF)

mqtt = MQTTClient(client_id="",
                  server=MQTT_BROKER,
                  user=MQTT_USER,
                  password=MQTT_PASS)

previous_level = 1

while True:
    try:
        if not wlan.isconnected():
            led_wifi.value(1)
            wlan.active(True)
            wlan.connect(WIFI_SSID, WIFI_PASS)
            while not wlan.isconnected():
                sleep(0.1)
            led_wifi.value(0)

        mqtt.connect()
        led_iot.value(0)

        current_level = BIN_CAPACITY - sensor.distance_cm()
        waste_added = current_level - previous_level
        previous_level = current_level
        
        if waste_added < 1:
            waste_added = 0

        data = {
            "bin_id": BIN_ID,
            "level": waste_added
        }

        mqtt.publish("b6510545641/waste", json.dumps(data))

    except Exception as e:
        print("Exception:", e)

    finally:
        mqtt.disconnect()
        led_iot.value(1)

    sleep(3600)
