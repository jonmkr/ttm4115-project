from stmpy import Machine, Driver

import ipywidgets as widgets
from IPython.display import display
import os
print(os.listdir())


class Charger:

    def load_images(self):
        self.start = open("ttm4115-project/charger/Electric_charger/images/green_on.png", "rb").read()
        self.reserve = open("ttm4115-project/charger/Electric_charger/images/yellow_on.png", "rb").read()
        self.stop = open("ttm4115-project/charger/Electric_charger/images/red_on.png", "rb").read()

    # Send a message to start charging
    def on_button_start(self, b_start):
        self.stm.send("start_charging")

    def on_button_reserve(self, b_reserve):
        self.stm.send("reserve_charger")

    def on_button_stop(self, b_stop):
        self.stm.send("stop_charger")

    def display(self):
        # Buttons
        self.button_start = widgets.Button(description="Start charging")
        self.button_start.on_click(self.on_button_start)

        self.button_reserve = widgets.Button(description="Reserve charger")
        self.button_reserve.on_click(self.on_button_reserve)

        self.button_stop = widgets.Button(description="Stop charger")
        self.button_stop.on_click(self.on_button_stop)

        # Text field to display states
        self.text = widgets.Text(value='', placeholder='', description='String:', disabled = False)
        display(self.text,  self.button_start, self.button_reserve, self.button_stop)


    def __init__(self):
        self.load_images()
        self.display()



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

#Transition from reserved to ban_user

t2 = {'trigger':'start_charging',
      'source':'reserved',
      'target':'ban_user'}

#Transition from availble to charging
t3 = {'trigger': 'start_charging',
      'source':'available',
      'target':'charging'}

#Transition from charging to finish_charging
t4 = {'trigger':'charging_stopped',
      'source': 'charging',
      'target':'finish_charging'}

#Transition from charging to charging_battery_full
t5 = {'trigger':'battery_full',
      'source':'charging',
      'target':'charging_battery_full'}

#Transition from charging_battery_full to finish_charging
t6 = {'trigger':'charging_stopped',
      'source':'charging_battery_full',
      'target':'finish_charging'}

#Transition from charging_battery_full to overcharge
t7 = {'trigger':'t1',
      'source':'charging_battery_full',
      'target':'overcharge'}

#Transition from overcharge to finish_charging
t8 = {'trigger':'charging_stopped',
      'source':'overcharge',
      'target':'finish_charging'}

#Transition from finish_charging to available
t9 = {'trigger':'charger_available',
      'source':'finish_charging',
      'target':'available'}

#Transition from ban_user to available
t10 = {'trigger':'charger_available',
       'source':'ban_user',
       'target':'available',
       'effect':'stop_timer("t1")'}


# STATES

available = {'name':'available'}

reserved = {'name':'reserved',
            'entry':'start_timer("t1", 150000)'}

ban_user = {'name':'ban_user',
            'entry':'user_timeout'}

charging = {'name':'charging',
            'entry':'start_payment; lock_plug; start_power'}

charging_battery_full = {'name':'charging_battery_full',
                         'entry':'start_timer("t2", 150000)'}

overcharge = {'name':'overcharge',
              'entry':'start_overchargepayment'}

finish_charging = {'name':'finish_charging',
                   'entry':'stop_power; stop_payment; stop_overchargepayment; unlock_plug; charge_customer;'}



machine = Machine(name="charger", transitions=[t0,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10], obj=charger, states=[available, reserved, ban_user, charging, charging_battery_full, overcharge, finish_charging])
charger.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()