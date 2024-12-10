from typing import Dict, List, Tuple
import math

class ViscousFlow:
    def __init__(self, viscosity: float, density: float):
        self.viscosity = viscosity
        self.density = density
        
    def calculate_reynolds_number(self, velocity: float, 
                                characteristic_length: float) -> float:
        return (self.density * velocity * characteristic_length) / self.viscosity
    
    def calculate_pressure_drop(self, length: float, diameter: float, 
                              flow_rate: float) -> float:
        velocity = flow_rate / (math.pi * (diameter/2)**2)
        reynolds = self.calculate_reynolds_number(velocity, diameter)
        
        if reynolds < 2300:
            friction_factor = 64 / reynolds
        else:
            friction_factor = 0.316 / reynolds**0.25
            
        return (friction_factor * length * self.density * velocity**2) / (2 * diameter)
    
    def calculate_shear_stress(self, velocity_gradient: float) -> float:
        return self.viscosity * velocity_gradient
    
    def solve_couette_flow(self, plate_velocity: float, 
                          plate_separation: float, 
                          num_points: int) -> List[Tuple[float, float]]:
        velocity_profile = []
        dy = plate_separation / (num_points - 1)
        
        for i in range(num_points):
            y = i * dy
            u = plate_velocity * y / plate_separation
            velocity_profile.append((y, u))
            
        return velocity_profile