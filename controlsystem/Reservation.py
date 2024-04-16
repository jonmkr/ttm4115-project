



from threading import Thread
import paho.mqtt.client as mqtt
import random
import json


CAPACITY = 10
MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
TOPIC = "ReservationProcedure"

class ChargingStation:
    
    def __init__(self):
        self.spot = [None] * CAPACITY
        self.free_spot = []


    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))


    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        
        # reservation code comes from Web Server throught Queue() function (Jon's writing the code)
        reservation_code = Queue()
        
        message = {
            "message" : "Spot Reserved - " + reservation_code,
            "reservation code" : reservation_code
        }
        
        try:
            self.client.publish(TOPIC, json.dumps(message))
        except:
            print("Unreserved spot")


    def start(self, broker, port):
        self.client = mqtt.Client(callback_api_version=2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)

        #TOPIC
        self.client.subscribe(TOPIC)

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
    
            
    
    def update_availability(self, spot_number, update_massage):
            # spot free -> none     spot reserved -> ""
            if update_massage is None:
                self.spot[spot_number] = None
            else:
                self.spot[spot_number] = ""
         
                
    ### TO DO ###
    
    # function to receve a http message with the reservation code from Web Server
    
    # function to receve a http message with the expiration time from Web Server
        