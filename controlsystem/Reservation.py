



from threading import Thread
import paho.mqtt.client as mqtt
import random


CAPACITY = 10
MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883

class ChargingStation:
    
    def __init__(self):
        self.spot = {i: None for i in range(CAPACITY)}
        self.free_spot = []


    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))


    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        
        random_index = self.reservation()
        try:
            self.client.publish("Reserved spot", msg.payload)
        except:
            print("Unreserved spot")


    def start(self, broker, port):
        self.client = mqtt.Client(callback_api_version=2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        #TOPIC
        self.client.subscribe("ttm4115")

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()
  
            
    def reservation(self, code_reservation):
        
        for index in range(CAPACITY):
            if self.spot[index] is None:
                self.free_spot.insert(index)
                
        if len(self.free_spot) == 0:
            return None
        else:
            random_index = random.choice(self.free_spot)
            self.free_spot.remove(random_index)
            self.spot[random_index] = str(code_reservation)
            
        return random_index
    
            
    
    def check_availability(self, random_index):
            if random_index is None:
                return None
            else:
                self.spot[random_index] = ""
         
                
    # function to reserve a spot
    def receive_http_request(self):
        # Handle the HTTP request and call the reserve_spot function
        self.reserve_spot()
        