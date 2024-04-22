

### TO DO ###
        
# 1
"""
We need a function that receives a message via HTTP and checks the message flag, if it has the flag (TOPIC=RESERVATION) 
I call the function 'reserve_spot', the 'reservation code' I have because we receive it with the HTTP message. 
After this function finishes executing we send a message via MQTT to the eletric charger. 
The other branch of the if will have the flag (TOPIC=FREEUP) and will take care of calling the function 'free_up_spot' 
where the number of the spot to be freed is given to us via message from the web server. 
            
if (msg["type"] == "RESERVATION):
    ....
elif (msg["type"] == "EXPIRATION):
    ....
elif (msg["type"] == "CONFIRMATION"):
    ....
elif (msg["type"] == "AVAILABILITY"):
    ....
else:
    ---ERROR MESSAGE---
            
"""
  
  
#2
"""
a function is needed to check the messages arriving via MQTT from the electric charger. these messages will have the flag 
(TOPIC=UPDATING) and within the if to check the flag the function 'update_availability' will be called, where the spot number 
is obtained via the MQTT message received

if (msg["topic flag"] == "UPDATING):
    ....
else:
    ---ERROR MESSAGE---
    
"""   






from threading import Thread
import paho.mqtt.client as mqtt
import random
import json
from queue import Queue

from websockets.sync.client import connect
from queue import Queue

STATION_NAME = "Elgeseter"
CAPACITY = 10
MQTT_PORT = 1883
MQTT_BROKER = "broker.hivemq.com"

input_queue = Queue()
output_queue = Queue()


class msg:
    """
    This is the format of the message that is sent in all three cases: 
    RESERVATION, UPDATING, FREEUP_SPOT
    
    """
    def __init__(self, text, available, reservation_code, spot_position, type_flag):
        self.msg = {
            # content of the message to be printed on the screen
            "message" : text,
            # number of available spots at charging station
            "available": available,
            # reservation code used to check and manage bookings 
            "reservation_code" : reservation_code,
            # spot index used to free the spot in case of end of charge or expired booking
            "spot_position" : spot_position,
            # flag indicating the type of message for HTTP communications (RESERVATION, EXPIRATION, AVAILABLE)
            "type" : type_flag
        }
        
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
            self.client.publish("Reserving", json.dumps(message))
        except:
            print("Unreserved spot")
            
        # This is for FreeUP Messages
        try:
            self.client.publish("FreeUp", "Free Spot Available")
        except:
            print("Error with the free up of a spot")


    def start(self):
        self.client = mqtt.Client(callback_api_version = mqtt.CallbackAPIVersion.VERSION1)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        # There are 3 topics: Reserving, Updating, FreeUP a spot
        self.client.subscribe("RESERVATION")
        self.client.subscribe("UPDAITING")
        self.client.subscribe("FREEUP")

        thread = Thread(target=self.client.loop_forever)
        thread.start()
  
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

        
    def reserve_spot(self, msg):
        """
        Function that takes the message received via http from the web server as input. 
        The value of the fild "reservation_code" is inserted into the 'spot' list at a random position among the available ones. 
        (How do I know which indices in the 'spot' list are available? The available 'spot' list 
        indices are inserted into the 'free spot' list)
        
        """

        # We update the available spots positions before reserve a spot
        self.update_free_spot_list()
                
        # We check if there are places available 
        if len(self.free_spot) == 0:
            msg["spot_position"] = None
            msg["message"] = "Spot NOT reserved. No spot is available"
            msg["available"] = 0
            msg["type"] = "RESERVATION"
            
        else:
            # We randomly choose a value within the list. 
            # This value is equivalent to the index of a free position within the 'spot' list.
            spot_number = random.choice(self.free_spot)
            
            # We remove the item we received from the 'free spot' list.
            # (By now that spot is no longer free)
            self.free_spot.remove(spot_number)
            
            # We place in the 'spot' list in position, chosen randomly, the 'reservation code' of the reservation
            self.spot[spot_number] = str(msg["reservation_code"])
            
            msg["spot_position"] = spot_number
            msg["message"] = "Spot reserved"
            msg["available"] = len(self.free_spot)
            msg["type"] = "RESERVATION"

              
    def cancel_reservation(self, msg):
        """
        This function receives the 'reservation code' and does a reservation check, when it finds 
        the reserved spot with that code it releases it because the reservation has expired
        
        """
        
        reservation_code = msg["reservation_code"]
        
        for i in range(len(self.spot)):
            if self.spot[i] == str(reservation_code):
                self.spot[i] = None
                
                self.update_free_spot_list()
                
                msg["available"] = len(self.free_spot)
                msg["spot_position"] = None
                msg["message"] = "Reservation Canceled"
                msg["type"] = "EXPIRATION"

    
    def free_up_spot(self, spot_number):
        """
        Function to clear a spot. 
        This can happen because the recharge has been completed or because the reservation has expired 
       
        """
        
        # The spot number is passed on via MQTT and HTTP messages
        self.spot[spot_number]=None
        
        # We update which places are available in the 'free spot' list
        self.update_free_spot_list()

    
    def update_availability(self, spot_number):
        """
        This function serves to confirm that the machine is in charge and thus changes 
        the value in the 'spot number' position in the 'spot' list from 'reservation code' to "" 
        (empty string)
        
        """
        self.spot[spot_number] = ""
         
        """
        we do not need to update the 'free spot' list because a spot has not become free, 
        but we have only received confirmation that the spot is in use
        """ 


def start_websocket(input_queue: Queue, output_queue: Queue, station: ChargingStation):
    with connect("ws://localhost:5000/ws") as ws:
        payload = {'type': 'HANDSHAKE', 'id': 1, 'name': STATION_NAME, 'max_capacity': CAPACITY, 'availability': CAPACITY}

        ws.send(json.dumps(payload))

        while True:
            try:
                input_queue.put(json.loads(json.loads(ws.recv(timeout=1))))
            except TimeoutError:
                pass
            
            if not output_queue.empty():
                ws.send(json.dumps(output_queue.get()))
            
            if not input_queue.empty():
                msg = input_queue.get()
                if msg['type'] == "RESERVATION":
                    print("Received reservation with code", msg['reservation_code'])
                    station.reserve_spot(msg)
                    output_queue.put(json.dumps(msg))
                elif msg['type'] == "EXPIRATION":
                    print("Cancel reservation (free up spot) for reservation with code", msg['reservation_code'])
                    station.cancel_reservation(msg)
                    output_queue.put(json.dumps(msg))

if __name__ == "__main__":
    station = ChargingStation()
    station.start()

    websocket_t = Thread(target=start_websocket, args=(input_queue, output_queue, station))
    websocket_t.start()
