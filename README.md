# EVSE Model
The evse_model repository includes two Python classes: (i) ElectricVehicles.py that models the charging and discharging behavior of an electric vehicle (EV), (ii) EVSE_class.py that emulates an electric vehicle supply equipment (EVSE) or the charging port. These classes can be instantiated with required parameter values to generate multiple "electric vehicle" agents and "EVSE" agents that can interact with each other through built-in methods. The "test_run.py" script in this repository provide a simple example demonstrating the use of these two classes to emulate the charging of an EV at a charging port. This readme file explains the steps in "test_run.py" while providing details about these classes during the process.

## Step 1: Loading and initializing the classes
Load:

`from evse_class import EVSE_class`

`from ElectricVehicles import ElectricVehicles`

Initialize:

`ev1 = ElectricVehicles(departure_time=1*60*60, vehicle_type='bev', arrival_time=1*60, initial_soc=0.1, target_soc=0.15, batterycapacity_kWh = 120.0)`

`evse_instance = EVSE_class(efficiency=0.99, Prated_kW=6.6, evse_id=1)`

An EV agent or object can be instantiated by providing the following name-value pairs:
1. `arrival_time` : relative time in seconds [reqd.]
2. `initial_soc` : state of charge (SOC) of the EV at the time of arrival as a fraction between 0.0 and 1.0 [reqd.]
3. `batterycapacity_kWh` : capacity of the EV battery pack in killowatt-hours [reqd.]
