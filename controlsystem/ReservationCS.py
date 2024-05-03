from threading import Thread
import paho.mqtt.client as mqtt
import random
import json
import asyncio
from io import BytesIO

from queue import Queue
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

STATION_NAME = "Elgeseter"
STATION_ID = 1
CAPACITY = 1
MQTT_PORT = 1883
MQTT_BROKER = "localhost"

input_queue = Queue()
output_queue = Queue()


class msg:
    """
    This is the format of the message that is sent in all the cases
    
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
            # flag indicating the type of message for HTTP communications (RESERVATION, EXPIRATION, CONFIRMATION) (CHARGE_OVER, DISCONNECTED)
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


    def on_connect(self, client, userdata, flags, rc, properties):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))


    def on_message(self, client, userdata, msg):
        print("on_message(): topic: {}".format(msg.topic))

        if msg.topic == "arrivals":
            
            msg = json.loads(msg.payload)
            # This is for Arrival Messages
            try:
                # We receive a message via MQTT from Electric Charger, from which we take the spot index and call the function 
                # update availability to change from '(reservation_code)' to '' (empty string)
                print("Car arrived at charger #" + str(msg['spot_position']))
                self.update_availability(msg["spot_position"])
                msg["type"] = "CONFIRMATION"
                msg["availability"] = len(self.free_spot)
                output_queue.put(msg)
            except Exception as e:
                print("Error with the occupation of a spot: ", e)
                
        elif msg.topic == "departures":

            msg = json.loads(msg.payload)
            
            # This is for Departure Messages
            try:
                # We receive a message via MQTT from Electric Charger, from which we take the spot index and call the function 
                # free_up_spot to change from '' (empty string) to None
                self.free_up_spot(msg["spot_position"])
                print("Car left the spot number #" + str(msg['spot_position']))
                msg['availability'] = len(self.free_spot)
                msg["type"] = "AVAILABILITY"
                output_queue.put(msg)
            except Exception as e:
                print("Error with the free up of a spot: ", e)
                
        """     
        elif msg.topic == "charge_status":
            
            msg = json.loads(msg.payload)
            
            # This is for Charge Status Message
            try:
                # We receive a message via MQTT from Electric Charger, that informs us if the charge is done or not
                msg["type"] = "CHARGE_OVER"
                msg["text"] = "Charge is over"
                output_queue.put(json.dumps(msg))
            except Exception as e:
                print("Error with the message about charging status: ", e)
                
        elif msg.topic == "car_disconnected":
            
            msg = json.loads(msg.payload)
            
            # This is for Car Disconnected Message
            try:
                # We receive a message via MQTT from Electric Charger, that the car is been disconnected
                self.free_up_spot(msg["spot_position"])
                msg["type"] = "DISCONNECTED"
                msg["text"] = "Car is been disconnected"
                output_queue.put(json.dumps(msg))
            except Exception as e:
                print("Error with the message about charging status: ", e)
       
        """  
    
    def start(self):
        self.client = mqtt.Client(callback_api_version = mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print("Connecting to {}:{}".format(MQTT_BROKER, MQTT_PORT))
        self.client.connect(MQTT_BROKER, MQTT_PORT)

        # Update controller's topics
        self.client.subscribe("arrivals")
        self.client.subscribe("departures")
        
        # Charging finished status
        self.client.subscribe("charge_status")
        
        # Car Disconnected message
        self.client.subscribe("car_disconnected")

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
        It returns the updated reservation message. 
        """

        # We update the available spots positions before reserve a spot
        self.update_free_spot_list()
                
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

        return msg
              
    def cancel_reservation(self, msg):
        """
        This function receives the 'reservation code' and does a reservation check, when it finds 
        the reserved spot with that code it releases it because the reservation has expired.
        It returns the updated message. 
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

        return msg


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

               

class Server(BaseHTTPRequestHandler):
    def do_GET(self):
        size = self.headers['Content-Length']
        payload = self.rfile.read(int(size))
        data = json.loads(payload)
        print(data)
        
        input_queue.put(data)

        self.send_response(200)
        self.end_headers()

def producer(output_queue: Queue):
    while True:
        payload = output_queue.get()
        payload['station_id'] = STATION_ID
        requests.get("http://localhost:5000/connect", json=payload)

def consumer(input_queue: Queue, station: ChargingStation):
    while True:
        msg = input_queue.get()
        if msg['type'] == "RESERVATION":
            print("Received reservation with code", msg['reservation_code'])
            msg = station.reserve_spot(msg)
            station.client.publish("reservations", json.dumps(msg))
        # EXPIRATION corresponds to 'free up spot' in sequence diagram 
        elif msg['type'] == "EXPIRATION":
            print("Reservation with code {} expired", msg['reservation_code'])
            msg = station.cancel_reservation(msg)
            station.client.publish("expirations", json.dumps(msg)) 

if __name__ == "__main__":
    station = ChargingStation()
    station.start()

    Thread(target=producer, args=(output_queue,)).start()
    Thread(target=consumer, args = (input_queue, station,)).start()

    handshake = {'type': 'HANDSHAKE', 
                 'name': STATION_NAME, 
                 'max_capacity': CAPACITY, 
                 'availability': CAPACITY}

    output_queue.put(handshake)

    server = HTTPServer(("", 8080), Server)
    print("Server initialized")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()