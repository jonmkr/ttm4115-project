from flask import Flask, request, redirect, render_template

app = Flask(__name__, template_folder="templates")

class Location:
    def __init__(self, name, max_capacity: int, availability=None):
        self.name = name
        self.max_capacity = max_capacity
        self.availability = availability if availability else max_capacity
        self.reservations = {}

locations = {1: Location('Elgeseter', 3), 5: Location('Solsiden', 10)}

@app.route("/locations")
@app.route("/locations/<int:location_id>")
def locations_handler(location_id=None):
    if location_id:
        return redirect(f"{location_id}/reservations")

    return render_template("locations.html", locations=locations)

@app.route("/locations/<int:location_id>/reservations", methods=['GET', 'POST', 'DELETE'])
def reservations_handler(location_id):
    if request.method == 'GET':
        if location_id not in locations:
            return f"Invalid location id", 404
        
        location = locations[location_id]
        return f"Availability {location.availability}/{location.max_capacity}"


    elif request.method == "POST":
        print("POST REQUEST")
