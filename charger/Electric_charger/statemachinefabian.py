from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display


class Charger:
    # Send a message to start charging
    def on_button_start(self, b_start):
        self.stm.send("start_charging")

    def on_button_reserve(self, b_reserve):
        self.stm.send("reserve_charger")

    def on_button_stop(self, b_stop):
        self.stm.send("stop_charger")



    def __init__(self):

        # Buttons
        self.button_start = widgets.Button(description="Start charging")
        self.button_reserve = widgets.Button(description="Reserve charger")
        
        # Text field to display states
        self.text = widgets.Text(value='', placeholder='', description='String:', disabled = False)
        display(self.text, self.button_start, self.button_reserve)


    def available(self):
        test = test

    def reserved(self):
        test = test

    def ban_user(self):
        test = test

    def charging(self):
        test = test
    
    def charging_battery_full(self):
        test = test

    def overcharge(self):
        test = test

    def finish_charging(self):
        test = test

charger = Charger()
#Initial transitiion
t0 = {'source':'initial',
      'target':'spinning'}

#Transition from available to reserved
t1 = {'trigger':'reserve_charger',
      'source':'available',
      'target':'reserved'}

#Transition from reserved to charging

t2 = {'trigger':'start_charging',
      'source':'reserved',
      'target':'ban_user'}

#Transition from availble to charging
t3 = {'trigger': 'start_charging',
      'source':'available',
      'target':'charging'}

#Transition from charging to finish_charging
t4 = {}

#Transition from charging to charging_battery_full
t5 = {}

#Transition from charging_battery_full to finish_charging
t6 = {}

#Transition from charging_battery_full to overcharge
t7 = {}

#Transition from finish_charging to available
t8 = {}






# STATES

machine = Machine(name="charger")