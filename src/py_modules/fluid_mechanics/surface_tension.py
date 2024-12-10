from typing import Dict, List, Tuple
import math

class SurfaceTensionCalculator:
    def __init__(self, surface_tension: float, contact_angle: float):
        self.surface_tension = surface_tension
        self.contact_angle = math.radians(contact_angle)
        
    def calculate_capillary_force(self, perimeter: float) -> float:
        return self.surface_tension * perimeter * math.cos(self.contact_angle)
    
    def calculate_droplet_shape(self, volume: float, gravity: float = 9.81e-6) -> Dict[str, float]:
        bond_number = (gravity * volume**(2/3)) / self.surface_tension
        
        if bond_number < 1:
            radius = (3 * volume / (4 * math.pi))**(1/3)
            height = 2 * radius
        else:
            radius = (volume / (math.pi * bond_number))**(1/3)
            height = volume / (math.pi * radius**2)
            
        return {
            "radius": radius,
            "height": height,
            "bond_number": bond_number,
            "surface_area": 2 * math.pi * radius * height + 2 * math.pi * radius**2
        }
    
    def calculate_meniscus_height(self, tube_radius: float, 
                                fluid_density: float, 
                                gravity: float = 9.81) -> float:
        return (2 * self.surface_tension * math.cos(self.contact_angle)) / \
               (fluid_density * gravity * tube_radius)