class EVSE_class():
    def __init__(self, efficiency, Prated_kW, evse_id):
        self.efficiency = efficiency
        self.Prated_kW  = Prated_kW
        self.evse_id   = evse_id

        self.ev_voltage = 0.0
        self.ev_power   = 0.0
        self.ev_soc     = 0.0
        self.ev_plugged = False

        self.server_setpoint = 0.0

       
    def receive_from_ev(self, Vbatt, Pbatt_kW, soc, plugged):
        self.ev_voltage = Vbatt
        self.ev_power   = Pbatt_kW
        self.ev_soc     = soc
        self.ev_plugged = plugged


    def send_to_ev(self):
        Pmax = min(self.server_setpoint, self.Prated_kW)*self.efficiency
        
        return Pmax


    def receive_from_server(self, setpoint_kW):
        self.server_setpoint = setpoint_kW


    def send_to_server(self):
        Vbatt    = self.ev_voltage
        Pbatt_kW = self.ev_power
        soc      = self.ev_soc
        
        return [Vbatt, Pbatt_kW, soc]

