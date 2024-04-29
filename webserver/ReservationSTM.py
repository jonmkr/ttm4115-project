import random
from stmpy import Machine, Driver
import ipywidgets as widgets
from IPython.display import display


class Reservation:

    #creating buttons for testing the STM
    def on_button_reserve(self, b):
        self.stm.send('Reserve')
        print("Slot is now reserved and you are in the Booked state")

    def on_button_plugIn(self, b):
        self.stm.send('PlugingIn')
        print("Slot is now pluged in at and you are in the Check In state")

    def on_button_leave(self, b):
        self.stm.send('Leaving')
        print("Car is now leaving the slot and you are in the Unbooked state")

    def t1_print(self):
        print("Timer has expired, you are now in Penalty state and cannot reserve for another 24 hours.")

    def t2_print(self):
        print("Penalty has ended, you are now in Unbooked state and can reserve spots again.")

    def __init__(self):
        # display the user interface
        # a button
        self.button_reserve = widgets.Button(description="Reserve")
        self.button_reserve.on_click(self.on_button_reserve)
        # another button
        self.button_plugIn = widgets.Button(description="Check in")
        self.button_plugIn.on_click(self.on_button_plugIn)
        # another button
        self.button_leaving = widgets.Button(description="Leaving")
        self.button_leaving.on_click(self.on_button_leave)
        
        # display everything
        display(self.button_reserve, self.button_checkIn, self.button_leaving)

    def generate_reservation_key(self):
        #There will not be more than 8999 cars making reservations at the same time, therfore this is okey for this system
        print(random.randint(1000, 10000))

reservation = Reservation()

##Transitions are written here
t0 = {'source': 'initial',
      'target': 'Unbooked'}

booking_placed = {'trigger': 'Reserve',
      'source': 'Unbooked',
      'target': 'Booked',
      'effect': 'generate_reservation_key()'}

left = {'trigger': 'Leaving',
      'source': 'Plugged_in',
      'target': 'Unbooked'}

plug_in = {'trigger': 'PlugingIn',
      'source': 'Booked',
      'target': 'Plugged_in'}

t1 = {'trigger': 't1',
      'source': 'Booked',
      'target': 'Penalty',
      'effect': 't1_print'}

t2 = {'trigger': 't2',
      'source': 'Penalty',
      'target': 'Unbooked',
      'effect': 't2_print'}

##Dicts for states written here
Unbooked = {'name': 'Unbooked'}

Booked = {'name': 'Booked',
       'entry': 'start_timer("t1", 5000)'
        }
#To make the system testable, we did not put this at 15 min (900000 ms)

Plugged_in = {'name': 'Plugged_in',
            'entry': 'stop_timer("t1")'}

Penalty = {'name': 'Penalty',
      'entry': 'start_timer("t2", 14400)'
      }
#To make the system testable, we did not put this at 24 hours (8.64e+7 ms)


##Creating and starting the machine
machine = Machine(name='reservation', 
                  transitions=[t0, t1, t2, booking_placed, left, plug_in], 
                  obj=reservation, 
                  states=[Unbooked, Booked, Plugged_in, Penalty])
reservation.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()
