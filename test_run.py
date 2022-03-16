from evse_class import EVSE_class
from ElectricVehicles import ElectricVehicles

import numpy as np

####################################################################
### Initialization
####################################################################
ev1 = ElectricVehicles(departuretime=4*60*60, vehicle_type='bev', arrival_time=30*60, initial_soc=0.1)
evse_instance = EVSE_class(efficiency=0.99, Prated_kW=6.6, evse_id=1)
evse_instance.server_setpoint = 10

ev1.assign_evse(evse_instance.evse_id)

t0 = 0
tf = 4.1*60*60
dt = 1

Pmax = 0.0

####################################################################
### Start simulation
####################################################################
for t in np.arange(t0, tf, dt):
    ev1.chargevehicle(t, dt=dt, evsePower_kW=Pmax)

    ### EV -> EVSE
    evse_instance.receive_from_ev(ev1.packvoltage, ev1.packpower, 
                                  ev1.soc, ev1.pluggedin, ev1.readytocharge)

         
    ### EVSE -> EV
    Pmax = evse_instance.send_to_ev()

    print('t:{0}, soc: {1}, plugged: {2}, Pmax:{3}'.format(t, ev1.soc, ev1.pluggedin, Pmax))
        