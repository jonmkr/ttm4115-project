import random
from stmpy import Machine, Driver
# import ipywidgets as widgets
# from IPython.display import display


class Reservation:

    def on_button_reserve(self, b):
        self.stm.send('Reserve')
        print("Slot is now reserved and you are in the Booked state")

    def on_button_checkIn(self, b):
        self.stm.send('CheckingIn')
        print("Slot is now checked in at and you are in the Check In state")

    def on_button_leave(self, b):
        self.stm.send('Leaving')
        print("Car is now leaving the slot and you are in the Unbooked state")

    def t1_print(self):
        print("Timer has expired, you are now in Penalty state and cannot reserve for another 24 hours.")

    def t2_print(self):
        print("Penalty has ended, you are now in Unbooked state and can reserve spots again.")

    # def __init__(self):
    #     # display the user interface
    #     # a button
    #     self.button_reserve = widgets.Button(description="Reserve")
    #     self.button_reserve.on_click(self.on_button_reserve)
    #     # another button
    #     self.button_checkIn = widgets.Button(description="Check in")
    #     self.button_checkIn.on_click(self.on_button_checkIn)
    #     # another button
    #     self.button_leaving = widgets.Button(description="Leaving")
    #     self.button_leaving.on_click(self.on_button_leave)
        
    #     # display everything
    #     display(self.button_reserve, self.button_checkIn, self.button_leaving)

    def generate_reservation_key(self):
        #There will not be more than 8999 cars making reservations at the same time, therfore this is okey for this system
        print(random.randint(1000, 10000))

##Transitions are written here
t0 = {'source': 'initial',
    'target': 'Unbooked'}

available_place = {'trigger': 'Reserve',
    'source': 'Unbooked',
    'target': 'Booked'}

left = {'trigger': 'Leaving',
    'source': 'Check_in',
    'target': 'Unbooked',
    'effect': 'invalidate_reservation()'}

check_in = {'trigger': 'CheckingIn',
    'source': 'Booked',
    'target': 'Check_in'}

t1 = {'trigger': 't1',
    'source': 'Booked',
    'target': 'Penalty',
    'effect': 'reservation_timeout()'}

t2 = {'trigger': 't2',
    'source': 'Penalty',
    'target': 'Unbooked'}

##Dicts for states written here
Unbooked = {'name': 'Unbooked'}

Booked = {'name': 'Booked',
    'entry': 'start_timer("t1", 5000)',
    'exit': 'stop_timer("t1")'
    }

Check_in = {'name': 'Check_in'}

Penalty = {'name': 'Penalty',
    'entry': 'start_timer("t2", 14400)'
    }

transitions = [t0, t1, t2, available_place, left, check_in]
states = [Unbooked, Booked, Check_in, Penalty]
