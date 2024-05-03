import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Queue
from random import choice
from string import ascii_uppercase
from time import sleep

import requests
from flask import Flask, make_response, redirect, render_template, request
from flask_sock import Sock
from reservation_stm import states, transitions
from simple_websocket import ConnectionClosed, Server
from stmpy import Driver, Machine

input_queue = Queue()
output_queue = Queue()

app = Flask(__name__, template_folder="templates")
sock = Sock(app)

users = dict()

class Reservation:
    def __init__(self, code, expiry):
        self.code = code
        self.expiry = expiry
        self.expired = False
        self.dangling = False

        self.stm = Machine('reservation', transitions, self, states)

        send_request({'type': 'RESERVATION', 'reservation_code': self.code})

    def reservation_timeout(self):
        print("Reservation", self.code, "expired")
        self.expired = True
        send_request({'type': 'EXPIRATION', 'reservation_code': self.code})

    def invalidate_reservation(self):
        print("Reservation", self.code, "set for removal")
        self.dangling = True

@dataclass
class Location:
    name: str
    max_capacity: int
    availability: int
    reservations: "dict[str: Reservation]" = field(default_factory=lambda: dict())

locations = {}

driver = Driver()
driver.start(keep_active=True)

from threading import Thread


def send_request(data):
    requests.get("http://localhost:8080", json=data)

@app.route("/connect")
def handshake():
    print("Received payload:", request.data)
    data = json.loads(request.data)
    station_id = data['station_id']

    if data['type'] == "HANDSHAKE":
        locations[station_id] = Location(data['name'], data['max_capacity'], data['availability'])
        print(data['name'], "added")

    elif data['type'] == "CONFIRMATION":
        code = data['reservation_code']
        try:
            locations[station_id].availability = data['availability']
            if code:
                locations[station_id].reservations[code].dangling = True
        except Exception as e:
            print(e)

    if data['type'] == "AVAILABILITY":
        avl = data['availability']
        try:
            locations[station_id].availability = avl
        except Exception as e:
            print(e)

    return ('', 200)

@app.route("/")
@app.route("/locations")
@app.route("/locations/<int:location_id>")
def locations_handler(location_id=None):
    if location_id:
        return redirect(f"{location_id}/reservations")

    return render_template("locations.html", locations=locations)

@app.route("/locations/<int:location_id>/reservations", methods=['GET'])
def reservations_handler(location_id):
    if request.method == 'GET':
        if location_id not in locations:
            return f"Invalid location id", 404

        location = locations[location_id]

        reservation_count = 0
        for code, reservation in location.reservations.items():
            if not reservation.expired:
                reservation_count += 1

            if reservation.dangling:
                reservation.stm.terminate()
                del location.reservations[code]

        reservation = None
        
        if 'CODE' in request.cookies:
            code = request.cookies.get('CODE')

            if code in location.reservations:
                reservation = location.reservations[code]

        
        template = render_template("reservations.html", location=location, reservation_count=reservation_count, reservation=reservation)

        response = make_response(template)

        if reservation is None:
            response.set_cookie("CODE", "", max_age=0)

        return response

@app.route("/locations/<int:location_id>/reservations/generate", methods=['GET'])
def generatation_handler(location_id):
    if location_id not in locations:
        return f"Invalid location id", 404
    
    location = locations[location_id]

    while True:
        code = "".join([choice(ascii_uppercase) for _ in range(4)])
        if code not in location.reservations:
            break
    
    expiry = datetime.now() + timedelta(minutes=15)

    reservation = Reservation(code, expiry)
    location.reservations[code] = reservation
    driver.add_machine(reservation.stm)

    reservation.stm.send('Reserve')

    response = make_response()
    response.set_cookie("CODE", code, expires=expiry + timedelta(hours=24))
    return response

if __name__ == "__main__":
    app.run()