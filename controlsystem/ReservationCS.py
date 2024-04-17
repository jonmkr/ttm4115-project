

from threading import Thread
import paho.mqtt.client as mqtt
import random
import json
from queue import Queue

CAPACITY = 10
MQTT_BROKER = "mqtt.item.ntnu.no"
MQTT_PORT = 1883
TOPIC = "ReservationProcedure"

class ChargingStation:
    
    def __init__(self):
        """
        The 'spot' list has three possible types of data within it:
        
        - 'None' -> When the spot is available
        - '' (empty string) -> When the spot is occupied (the presence of a car in that spot has been confirmed)
        - '(reservation code)' -> When the spot is reserved and the reserving car has the value in 'reservation code' variable
        
        """
        # at the begginig of the program, all spots are available (all spots are None)
        self.spot = [None] * CAPACITY
        # this list is used to keep track of the free spots
        self.free_spot = []


    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))


    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))
        
        # reservation code comes from Web Server throught Queue() function (Jon's writing the code)
        reservation_code = Queue()
        reserved_spot = self.reservation(reservation_code)
        
        message = {
            "message" : "Spot Reserved - " + reservation_code,
            "reservation code" : reservation_code,
            "reserved spot" : reserved_spot
        }
        
        # This is for Reservating Messages
        try:
            self.client.publish(TOPIC + "/Reserving", json.dumps(message))
        except:
            print("Unreserved spot")
            
        # This is for FreeUP Messages
        try:
            self.client.publish(TOPIC + "/FreeUp", "Free Spot Available")
        except:
            print("Error with the free up of a spot")


    def start(self):
        self.client = mqtt.Client(callback_api_version = mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        # There are 3 topics: Reserving, Updating, FreeUP a spot
        # I want that CS is subsribed in all three
        self.client.subscribe(TOPIC + "/")

        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()
  
###----------------------------------------------------------------------------------------------------###  

    def update_free_spot_list(self): 
        """
        Let's scroll the 'spot' list.
        For all elements that have the value 'None' 
        we add their index to the 'free spot' list. 
        
        """
        
        # Each time we use this function we reset the contents of the 'free spot' list. 
        # Each time we perform the check in its entirety
        self.free_spot=[]
        
        for index in range(CAPACITY):
            if self.spot[index] is None:
                self.free_spot.append(index)

        
    def reserve_spot(self, code_reservation):
        """
        Function that takes the 'reservation code' received via http from the web server as input. 
        This value is inserted into the 'spot' list at a random position among the available ones. 
        (How do I know which indices in the 'spot' list are available? The available 'spot' list 
        indices are inserted into the 'free spot' list)
        
        """

        # We update the available spots positions before reserve a spot
        self.update_free_spot_list()
                
        # We check if there are places available 
        if len(self.free_spot) == 0:
            return None
        else:
            # We randomly choose a value within the list. 
            # This value is equivalent to the index of a free position within the 'spot' list.
            spot_number = random.choice(self.free_spot)
            
            # We remove the item we received from the 'free spot' list.
            # (By now that spot is no longer free)
            self.free_spot.remove(spot_number)
            
            # We place in the 'spot' list in position, chosen randomly, the 'reservation code' of the reservation
            self.spot[spot_number] = str(code_reservation)
            
        return spot_number
    
    
    def free_up_spot(self, spot_number):
        #Function with spot number as input, and frees up the spot in the lists in the control system
        self.spot[spot_number]=None
        self.update_free_spot_list()

    
    def update_availability(self, spot_number, update_massage):
            # spot free -> none     spot reserved -> ""
            if update_massage is None:
                self.spot[spot_number] = None
            else:
                self.spot[spot_number] = ""
         
                
    ### TO DO ###
    
    # function to receve a http message with the reservation code from Web Server
    
    # function to receve a http message with the expiration time from Web Server
        