from typing import Dict, List, Tuple
import math

def calculate_orbital_period(semi_major_axis: float, central_mass: float) -> float:
    G = 6.67430e-11
    return 2 * math.pi * math.sqrt(semi_major_axis**3 / (G * central_mass))

def calculate_escape_velocity(mass: float, radius: float) -> float:
    G = 6.67430e-11
    return math.sqrt(2 * G * mass / radius)

def calculate_gravitational_force(mass1: float, mass2: float, 
                               distance: float) -> float:
    G = 6.67430e-11
    return G * mass1 * mass2 / (distance * distance)

def calculate_relativistic_time_dilation(velocity: float, 
                                       proper_time: float) -> float:
    c = 299792458
    gamma = 1 / math.sqrt(1 - (velocity * velocity) / (c * c))
    return proper_time * gamma

def calculate_radiation_shielding(material_thickness: float, 
                                material_density: float, 
                                radiation_energy: float) -> float:
    attenuation_coefficient = 0.5  # Simplified coefficient
    return math.exp(-attenuation_coefficient * material_density * material_thickness)