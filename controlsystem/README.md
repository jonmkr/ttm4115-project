# Component Description
The Control System component emulates a central control system found at one of many charging stations. The control system manages the stations metadata, which it exchanges in the handshake with the webserver. Additionally, the control system manages and forwards reservation codes to on-site electric chargers.

# Installation and Execution
Dependencies can be installed by running the terminal command below.
`python -m pip install -r requirements.txt`
A local MQTT server is required to be running on localhost and the default port. Mosquitto is recommended.

The application may be run using the following terminal command below.
`python main.py`