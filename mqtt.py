import paho.mqtt.client as mqtt
from threading import Thread

class MQTTClient:
    def __init__(self):
        self.client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect

    def on_connect(self, client, userdata, flags, rc, payload):
        print("Connected")

    def start(self):
        self.client.connect("broker.hivemq.com")

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            self.client.disconnect()

client = MQTTClient().start()

while True:
    pass
