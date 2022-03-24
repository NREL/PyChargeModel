from evse_class import EVSE_class
from ElectricVehicles import ElectricVehicles

import numpy as np

####################################################################
### Initialization
####################################################################
ev1 = ElectricVehicles(departure_time=1*60*60, vehicle_type='bev', arrival_time=1*60, initial_soc=0.1, target_soc=0.15, batterycapacity_kWh = 120.0)
evse_instance = EVSE_class(efficiency=0.99, Prated_kW=6.6, evse_id=1)
evse_instance.server_setpoint = 10

ev1.assign_evse(evse_instance.evse_id)

t0 = 0
tf = 1.1*60*60
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

    print('t:{0}, soc:{1}, plugged:{2}, Pmax [kW]:{3}, Pevse from grid [W]:{4}, Pevse to EV [W]:{5}'.format(
           t, ev1.soc, ev1.pluggedin, Pmax, evse_instance.ev_power/evse_instance.efficiency, evse_instance.ev_power))
        