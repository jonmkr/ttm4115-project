from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display


class Charger:
    # Send a message to start charging
    def on_button_start(self, b_start):
        self.stm.send("start_charging")

    def on_button_reserve(self, b_reserver):
        self.stm.send("reserve_charger")


    def __init__(self):

        # Buttons
        self.button_start = widgets.Button(description="Start charging")
        self.button_reserve = widgets.Button(description="Reserve charger")
        
        # Text field to display states
        self.text = widgets.Text(value='', placeholder='', description='String:', disabled = False)
        display(self.text, self.button_start, self.button_reserve)


    def available():
        test = test

    def reserved():
        test = test

    def ban_user():
        test = test

    def charging():
        test = test
    
    def charging_battery_full():
        test = test

    def overcharge():
        test = test

    def finish_charging():
        test = test

charger = Charger()
#Initial transitiion
t0 = {'source':'initial',
      'target':'spinning'}

#Transition from available to reserved
t1 = {'trigger':'reserve_charger',
      'source':'available',
      'target':'reserved'}

#Transition from availble to charging
t2 = {'trigger': 'start_charging',
      'source':'available',
      'target':'charging'}

#Transition from  



# STATES

machine = Machine(name="charger")