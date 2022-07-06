# -*- coding: utf-8 -*-
"""
Created on Wed Feb 23 09:32:13 2022

@author: pmishra
"""

import os
import pandas as pd
import numpy as np
from scipy import interpolate
import math

class ElectricVehicles:
    def __init__(self, **kwargs):
        # load EV parameters
        kwargs =  {k.lower(): v for k, v in kwargs.items()}
        if 'vehicle_type' in kwargs:
            self.evtype = kwargs['vehicle_type']
        else:
            self.evtype = 'bev'

        self.arrivaltime = kwargs['arrival_time']
        self.initialsoc = kwargs['initial_soc']
        self.modelparameters = self.load_ev_file(**kwargs)
        if 'batterycapacity_kwh' in kwargs:
            self.modelparameters['ev_packcapacity'] = kwargs['batterycapacity_kwh']
        self.soc = self.initialsoc
        self.timestamp_soc = self.arrivaltime
        self.packvoltage = self.getocv(self.soc, **kwargs)[0]
        self.packpower = 0.0
        self.packcurrent = 0.0
        self.pluggedin = False
        self.readytocharge = False
        self.chargecomplete = False
        if 'target_soc' in kwargs:
            self.targetsoc = kwargs['target_soc']
        else:
            self.targetsoc = 1.0 # if target SOC is not provided, set it as 1.0
        if 'departure_time' in kwargs:
            self.departuretime = kwargs['departure_time']
        else:
            self.departuretime = self.arrivaltime + 24.0*3600 # if departure time is not provided, set it as 24 hours later than arrival time
        self.evse_id = np.nan
        
        
        
        
    def isvehiclepluggedin(self,simulationtime):
        # method to check if a vehicle is plugged in or not
        if (simulationtime >= self.arrivaltime) and (simulationtime < self.arrivaltime + self.modelparameters['ev_setuptime']) and (simulationtime <= self.departuretime):
            self.pluggedin = True
            self.readytocharge = False
            
        elif (simulationtime >= self.arrivaltime + self.modelparameters['ev_setuptime']) and (simulationtime <= self.departuretime):
            self.pluggedin = True
            self.readytocharge = True
        else:
            self.pluggedin = False
            self.readytocharge = False
        
        
    def assign_evse(self,evse_id):
        self.evse_id = evse_id
            
    def ischargecomplete(self, simulationtime, **kwargs):
        if simulationtime >= self.departuretime or self.soc >= self.targetsoc:
            self.chargecomplete = True
        else:
            self.chargecomplete = False
        
        
    def load_ev_file(self, **kwargs):
        # loads model paramaters either from a CSV file or defines default values
        if 'input_path' in kwargs:
            ev_parameters_file = os.path.join(kwargs['input_path'], 'evtype', '{}_parameters.csv'.format(self.evtype))
        
            params = pd.read_csv(ev_parameters_file, index_col = 'Parameter Name')
            params = params['Parameter Value'].astype(float).to_dict()
        else:
            print('Warning: Cannot find EV parameter file. Using default values for fixed parameters')
            params = {'ev_crate': 1.0, #1/hr
                      'ev_cellcapacity': 26.0, #Ah
                      'ev_packcapacity': 100.0, #kWh
                      'ev_nominalvoltage': 350.0, #V
                      'ev_setuptime': 30.0, #s
                      'ev_batterychemistry': 'nmc',
                      'ev_chargingprotocol':'cc-cv',
                      }
            
        return params
    
    def getocv(self,soc, **kwargs):
        # computes pack level open circuit voltage
        # get cell level ocv-soc curve based on battery chemistry
        if self.modelparameters['ev_batterychemistry'] == 'nmc':
            ocvpts = np.array([3.067,3.477,3.560,3.616,3.650,3.690,3.754,3.854,3.954,4.067,4.192])
            socpts = np.linspace(0.0, 1.0, num = ocvpts.size)
            rohmpts = np.array([0.00172,0.00154,0.00147,0.00141,0.001395,0.00137,0.00140,0.00150,0.00148,0.00145,0.00144])
            
        elif self.modelparameters['ev_batterychemistry'] =='lfp': # Data is for a 10Ah cell
            ocvpts = np.array([2.1434, 3.2048, 3.2593, 3.2927, 3.3068, 3.3119, 3.3223, 3.3386, 3.3447, 3.3486,3.5291])
            socpts = np.linspace(0.0, 1.0, num = ocvpts.size)
            rohmpts = np.array([3.1092,2.6633,1.8337,1.6094,1.5160,1.4196,1.3201,1.2206,1.2115,1.1838,1.2777])*1.0e-3
            #  Data Source: % Source: L.Lu, X. Han, J. Li, J. Hua, M. Ouyang,
            #  "A review on the key issues for lithium-ion battery management in electric vehicles",Journal of Power Sources, 2013, 226, 272-288 

        elif self.modelparameters['ev_batterychemistry'] =='lto':
            ocvpts = np.array([1.8219,2.1321,2.1633,2.1844,2.2058,2.2343,2.2726,2.3253,2.3995,2.4874,2.8158])
            socpts = np.linspace(0.0, 1.0, num = ocvpts.size)
            rohmpts = np.array([5.6123,3.0693,2.3927,2.1543,2.0235,2.0338,2.1051,2.0431,2.1884,2.3383,2.5148])*1.0e-3
            # Data source: A.I. Stroe, J. Meng, D.I Stroe et al., "Influence of Battery Parametric Uncertainties on the State-of-Charge
            # Estimation of Lithium Titanate Oxide-Based Batteries", Energies
            # 2018, 11, 795.
        else:
            ocvpts = np.array([3.067,3.477,3.560,3.616,3.650,3.690,3.754,3.854,3.954,4.067,4.192])
            socpts = np.linspace(0.0, 1.0, num = ocvpts.size)
            rohmpts = np.array([1.7359,1.6166,1.5263,1.4793,1.6639,1.6109,1.6389,1.5716,1.6222,1.0595,0.4736])*1.0e-3
        
        # Calculate battery configuration xSyP
        Ns = round(self.modelparameters['ev_nominalvoltage']/interpolate.pchip_interpolate(socpts, ocvpts, 0.5))
        Np = math.ceil((self.modelparameters['ev_packcapacity']*1.0e3)/(self.modelparameters['ev_nominalvoltage']*self.modelparameters['ev_cellcapacity']))
        packocv = Ns*interpolate.pchip_interpolate(socpts, ocvpts, soc)
        packresistance = Ns*interpolate.pchip_interpolate(socpts, rohmpts, soc)/Np
        return packocv, packresistance, Ns, Np, ocvpts, socpts, rohmpts
    
    def getvehiclestate(self):
        # obtains the vehicle states
        vehiclestate = {'soc': self.soc,
                        'packpower': self.packpower,
                        'packcurrent': self.packcurrent,
                        'packvoltage': self.packvoltage,
                        'pluginsignal': self.pluggedin,
                        'chargecompletesignal': self.chargecomplete,
                        'timestamp_soc': self.timestamp_soc}
        return vehiclestate
    
    def chargevehicle(self, simulationtime, **kwargs):
        self.isvehiclepluggedin(simulationtime)
        self.ischargecomplete(simulationtime)
        dt = kwargs['dt'] # in seconds
        
        if self.readytocharge and ~np.isnan(self.evse_id) and (not self.chargecomplete):
            # vehicle is ready to charge and assigned to an EVSE
            packocv, packresistance, Ns, Np, ocvpts, socpts, rohmpts  = self.getocv(self.soc)
            CVvolt = Ns*interpolate.pchip_interpolate(socpts,ocvpts,0.95)
            CCcurr = Np*self.modelparameters['ev_crate']*self.modelparameters['ev_cellcapacity']
            # assuming that EVSE will communicate a power with kW in the keyword 
            power = [keyval for key, keyval in kwargs.items() if 'kw' in key.lower()]
            if not power:
                current = CCcurr
            else:
                tempcurrent = (-packocv + math.sqrt(packocv**2 + 4.0*packresistance*power[0]*1.0e3))/(2.0*packresistance)
                if power[0] >= 0.0: # i.e. charging
                    current = min(CCcurr, tempcurrent)
                else:
                    current = max(CCcurr, tempcurrent)
            socnow = self.soc
            Vtemp = packocv + current*packresistance
            if Vtemp <= CVvolt:
                self.packcurrent = current
                self.packvoltage = packocv + current*packresistance
                self.packpower = self.packcurrent*self.packvoltage
                self.soc = socnow + (dt/3600.0)*current/(Np*self.modelparameters['ev_cellcapacity'])
                self.timestamp_soc = simulationtime + dt
            else:
                CVcurr = (CVvolt - packocv)/packresistance
                self.soc = socnow + (dt/3600.0)*CVcurr/(Np*self.modelparameters['ev_cellcapacity'])
                self.timestamp_soc = simulationtime + dt
                self.packcurrent = CVcurr
                self.packvoltage = CVvolt
                self.packpower = CVcurr*CVvolt
                
        else:
            # don't charge yet
            self.soc = self.soc
            self.packcurrent = 0.0
            self.packpower = 0.0
            self.packvoltage = self.packvoltage
            self.timestamp_soc = simulationtime + dt
            
            
            
                