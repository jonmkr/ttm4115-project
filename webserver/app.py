import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from queue import Queue
from random import choice
from string import ascii_uppercase
from time import sleep

from flask import Flask, make_response, redirect, render_template, request
from flask_sock import Sock
from reservation_stm import states, transitions
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

        output_queue.put(json.dumps({'type': 'RESERVATION', 'code': self.code}))

    def reservation_timeout(self):
        print("Reservation", self.code, "expired")
        self.expired = True
        output_queue.put(json.dumps({'type': 'EXPIRATION', 'code': self.code}))

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

@sock.route("/ws")
def websocket(ws):
    data = ws.receive()
    payload = json.loads(data)

    location_id = payload.pop('id')
    locations[location_id] = Location(payload['name'], payload['max_capacity'], payload['availability'])

    print(payload['name'] + " added")

    while True:
        recv = ws.receive(timeout=1)
        if recv is not None:
            input_queue.put(json.loads(recv))

        if not output_queue.empty():
            ws.send(json.dumps(output_queue.get()))
        
        if not input_queue.empty():
            msg = json.loads(json.loads(input_queue.get()))
            if msg['type'] == "CONFIRMATION":
                code = msg['reservation_code']
                try:
                    locations[location_id].reservations[code].dangling = True
                except Exception as e:
                    print(e)

            if msg['type'] == "AVAILABILITY":
                avl = msg['availability']
                try:
                    locations[location_id].availability = avl
                except Exception as e:
                    print(e)

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
        
        print(request.cookies)
        if 'CODE' in request.cookies:
            code = request.cookies.get('CODE')

            if code in location.reservations:
                reservation = location.reservations[code]

        print("Reservation:", reservation)
        
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
    try:
        app.run()
    except KeyboardInterrupt:
        pass