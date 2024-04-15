import paho.mqtt.client as mqtt
from threading import Thread


class MQTTClient:
    def __init__(self):
        pass

    def on_connect(self):
        pass

    def start(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect()

        try:
            thread = Thread.start(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            self.client.disconnect()