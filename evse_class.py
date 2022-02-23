class EVSE_class():
    def __init__(self, efficiency, Prated_kW):
        self.efficiency = efficiency
        self.Prated_kW  = Prated_kW
        
        self.ev.voltage = 0.0
        self.ev.power   = 0.0
        self.ev.soc     = 0.0
        self.ev.plugged = False
        
        self.server.setpoint = 0.0
       
    def receive_from_ev(self, Vbatt, Pbatt_kW, soc, plugged):
        self.ev.voltage = Vbatt
        self.ev.power   = Pbatt_kW
        self.ev.soc     = soc
        self.ev.plugged = plugged
        
    def send_to_ev(self):
        Pmax = min(self.server.setpoint, self.Prated_kW)*self.efficiency
        
        return Pmax
        
    def receive_from_server(self, setpoint_kW):
        self.server.setpoint = setpoint_kW
        
    def send_to_server(self):
        Vbatt    = self.ev.voltage
        Pbatt_kW = self.ev.power
        soc      = self.ev.soc
        
        return [Vbatt, Pbatt_kW, soc]