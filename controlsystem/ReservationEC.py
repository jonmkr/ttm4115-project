

from threading import Thread
import paho.mqtt.client as mqtt
import random
import json

CAPACITY = 10
MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
TOPIC = "ReservationProcedure"

TIME = True

class EletricCharger:
    
    def __init__(self):
        self.spot = [None] * CAPACITY


    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))


    def on_message(self, client, userdata, msg):
        
        # Charging Station seds a message in dictionary format
        msg_json = json.loads(msg.payload.decode())
        
        # Use the reservation code sent by dictionaty
        reservation_code = msg_json["reservation_code"]
        
        print("Reservation code - ", reservation_code)
        
        # I used a TIME variable to simulate the time of the car arriving
        # If it's true the car is arrived and the reservation is confirmed
        # if it's false the car is not arrived and the reservation is not confirmed
        # Both procedure send the message to Charging Station
        if TIME :
            try:
                self.client.publish(TOPIC + "/Updating", "Car Arrived")
            except:
                print("Unreserved spot")
        else:
            try:
                self.client.publish(TOPIC + "/Updating", "Car NOT Arrived")
            except:
                print("Unreserved spot")


    def start(self):
        self.client = mqtt.Client(callback_api_version=2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        # There are 3 topics: Reserving, Updating, Free a spot
        # I want that EC is subsribed in all three
        self.client.subscribe(TOPIC + "/")

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")s
            self.client.disconnect()