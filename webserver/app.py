from flask import Flask, request, redirect, render_template, make_response
from random import choice
from string import ascii_uppercase
from datetime import datetime, timedelta
from dataclasses import dataclass, field

app = Flask(__name__, template_folder="templates")

@dataclass
class Reservation:
    code: str
    expiry: datetime

@dataclass
class Location:
    name: str
    max_capacity: int
    availability: int
    reservations: "dict[str: Reservation]" = field(default_factory=lambda: dict())

locations = {1: Location('Elgeseter', 3, 3), 5: Location('Solsiden', 10, 10)}

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
        
        reservation = None
        location = locations[location_id]
        print(location.reservations)
        if 'CODE' in request.cookies:
            code = request.cookies.get('CODE')
            reservation = location.reservations.get(code)
            print(reservation)

        return render_template("reservations.html", location=location, reservation=reservation)

    elif request.method == "POST":
        print("POST REQUEST")

@app.route("/locations/<int:location_id>/reservations/generate", methods=['GET'])
def generatation_handler(location_id):
    if location_id not in locations:
        return f"Invalid location id", 404
    
    location = locations[location_id]

    while True:
        code = "".join([choice(ascii_uppercase) for _ in range(4)])
        if code not in location.reservations:
            break
    
    location.reservations[code] = Reservation(code, datetime.now() + timedelta(minutes=15))

    response = make_response(code)
    response.set_cookie("CODE", code, expires=datetime.now() + timedelta(hours=24, minutes=15))
    return response


