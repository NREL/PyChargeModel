# EVSE Model
The evse_model repository includes two Python classes: (i) ElectricVehicles.py that models the charging and discharging behavior of an electric vehicle (EV), (ii) EVSE_class.py that emulates an electric vehicle supply equipment (EVSE) or the charging port. These classes can be instantiated with required parameter values to generate multiple "electric vehicle" agents and "EVSE" agents that can interact with each other through built-in methods. The "test_run.py" script in this repository provide a simple example demonstrating the use of these two classes to emulate the charging of an EV at a charging port. This readme file explains the steps in "test_run.py" while providing details about these classes during the process.

## Step 1: Loading and initializing the classes
Load:

`from evse_class import EVSE_class`

`from ElectricVehicles import ElectricVehicles`

Initialize:

`ev1 = ElectricVehicles(departure_time=1*60*60, vehicle_type='bev', arrival_time=1*60, initial_soc=0.1, target_soc=0.15, batterycapacity_kWh = 120.0)`

`evse_instance = EVSE_class(efficiency=0.99, Prated_kW=6.6, evse_id=1)`

An EV agent or object can be instantiated by providing the following key-value pairs:
1. `arrival_time` : relative time of arrival of the vehicle in seconds [reqd.]
2. `initial_soc` : state of charge (SOC) of the EV at the time of arrival as a fraction between 0.0 and 1.0 [reqd.]
3. `batterycapacity_kWh` : capacity of the EV battery pack in killowatt-hours, default = 100 kWh [opt. but highly suggested]
4. `vehicle_type` : vehicle type to define the class of the vehicle, default = 'bev' [opt.]
5. `departure_time` : relative time of departure of the vehicle in seconds, default = arrival_time + 24 hours [opt.]
6. `target_soc` : target SOC for the vehicle to be charged up to, default = 1.0 [opt.]

There are other default parameters that can be further modified by providing a CSV file name and its input path where such parameter values can be listed. An example of such a file is included in this repo.

Similarly, an EVSE agent or object can be instantiated by providing the following key-value pairs:
1. `evse_id` : A numerical EVSE ID [reqd.]
2. `efficiency` : Efficiency of the EVSE as a fraction between 0 and 1 [reqd.]
3. `Prated_kW` : Rated power capacity of the EVSE in kW [reqd.]
The EVSE model is also compatible for smart charge management application. The power dispensed by the EVSE can be controlled by setting:
`evse_instance.server_setpoint = 5.0`

## Step 2: Assign the EV to an EVSE
An EVSE object is assigned to an EV object using the `assign_evse` method and passing on the EVSE ID:

`ev1.assign_evse(evse_instance.evse_id)`

## Step 3: Charge the EV
EV charging behavior is emulated by calling the `chargevehicle` method for each of the EV objects. The `chargevehicle` method is called at each time step during the simulation time. Thus this method updates the state of the EV over a single time step. In order to get a temporal profile of the vehicle charging power, SOC etc., this method needs to be called throughout the simulation time. In the `test_run.py` script, the EV is charged over the simulation period by running a for-loop:

`t0 = 0 #start of simulation time [s]`

`tf = 1.1*60*60 # end of simulation time [s]`

`dt = 1 # time step [s]`

`Pmax = 0.0 # maximum power to charge with [kW]`

`### Start simulation`

`for t in np.arange(t0, tf, dt):`
    `ev1.chargevehicle(t, dt=dt, evsePower_kW=Pmax)`

The `chargevehicle` method takes the following inputs:
1. t : simulation time in seconds as a numerical value
2. dt = x.x : timestep of simulation in seconds
3. evsePower_kW = x.xx : power to charge the vehicle with in kW [opt.]

Power setpoint by the EVSE (here `evsePower_kW`) is optional - without this input, the charging power requested by the EV is based on its power rating (i.e. rated C-rate). The model is also capable of handling charging and discharging behavior and this can be achieved by providing a positive or negative power setpoint while calling the `chargevehicle` method. 

## Step 4: Logging data

Throughout the simulation, various states of the EV object gets updated and these states can be accessed using the `getvehiclestate` method. Calling this method using `ev1.getvehiclestate()` returns a dictionary with the following keys:

1. `soc` : current state of charge of the EV [0-1]
2. `packpower` : power consumption at the battery pack terminals [W]
3. `packvoltage` : terminal voltage of the battery pack [V]
4. `packcurrent` : current drawn at the battery pack terminals [A]
5. `pluginsignal` : boolean indicating EV is plugged-in
6. `chargecompletesignal` : boolean indicating whether a charging session is completed or not
7. `timestamp_soc` : relative timestamps associated with the SOC of the battery pack [s]
