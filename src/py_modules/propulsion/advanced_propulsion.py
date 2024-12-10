from typing import Dict, List, Tuple
import math

class PropulsionSystem:
    def __init__(self, thrust: float, specific_impulse: float, mass_flow: float):
        self.thrust = thrust
        self.specific_impulse = specific_impulse
        self.mass_flow = mass_flow
        self.total_impulse = 0
        
    def calculate_delta_v(self, initial_mass: float, final_mass: float) -> float:
        g0 = 9.81
        return self.specific_impulse * g0 * math.log(initial_mass / final_mass)
    
    def calculate_burn_time(self, required_delta_v: float, 
                          spacecraft_mass: float) -> float:
        g0 = 9.81
        return spacecraft_mass * (1 - math.exp(-required_delta_v / 
                                             (self.specific_impulse * g0))) / self.mass_flow

class IonEngine(PropulsionSystem):
    def __init__(self, voltage: float, ion_mass: float, efficiency: float):
        self.voltage = voltage
        self.ion_mass = ion_mass
        self.efficiency = efficiency
        
        exhaust_velocity = math.sqrt(2 * self.voltage * 1.60217663e-19 / 
                                   (self.ion_mass * 1.66053907e-27))
        specific_impulse = exhaust_velocity / 9.81
        
        super().__init__(0.5, specific_impulse, 1e-6)
        
    def calculate_power_requirement(self, thrust: float) -> float:
        return 0.5 * thrust * self.specific_impulse * 9.81 / self.efficiency
    
    def optimize_trajectory(self, distance: float, 
                          time_constraint: float) -> Dict[str, float]:
        power = self.calculate_power_requirement(self.thrust)
        acceleration = self.thrust / (1000 + self.mass_flow * time_constraint)
        
        coast_time = math.sqrt(2 * distance / acceleration)
        burn_time = time_constraint - coast_time
        
        return {
            "power_required": power,
            "burn_time": burn_time,
            "coast_time": coast_time,
            "final_velocity": acceleration * burn_time
        }