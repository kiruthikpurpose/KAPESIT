import math
from datetime import datetime
from typing import Dict, List, Tuple

class PlanetaryConditions:
    def __init__(self, gravity: float, temperature: float, atmosphere_composition: Dict[str, float]):
        self.gravity = gravity
        self.temperature = temperature
        self.atmosphere_composition = atmosphere_composition

    def calculate_habitability_score(self) -> float:
        # Basic habitability calculation based on Earth-like conditions
        temp_score = 1 - abs(self.temperature - 288) / 288  # 288K is ~15°C
        gravity_score = 1 - abs(self.gravity - 9.81) / 9.81
        
        # Atmosphere scoring
        atmosphere_score = 0
        if "O2" in self.atmosphere_composition:
            atmosphere_score += self.atmosphere_composition["O2"] * 0.5
        if "N2" in self.atmosphere_composition:
            atmosphere_score += self.atmosphere_composition["N2"] * 0.3
        
        return (temp_score + gravity_score + atmosphere_score) / 3

class SpaceSimulationEngine:
    def __init__(self):
        self.planetary_data = {}

    def simulate_planetary_conditions(self, 
                                   planet_name: str,
                                   distance_from_star: float,
                                   planet_mass: float,
                                   star_luminosity: float) -> PlanetaryConditions:
        # Basic planetary condition calculations
        gravity = self.calculate_surface_gravity(planet_mass)
        temperature = self.estimate_surface_temperature(distance_from_star, star_luminosity)
        atmosphere = self.generate_basic_atmosphere()
        
        conditions = PlanetaryConditions(gravity, temperature, atmosphere)
        self.planetary_data[planet_name] = conditions
        return conditions

    def calculate_surface_gravity(self, mass: float) -> float:
        G = 6.67430e-11  # gravitational constant
        radius = math.pow(mass / 5520, 1/3)  # rough estimate using Earth's density
        return G * mass / (radius * radius)

    def estimate_surface_temperature(self, distance: float, luminosity: float) -> float:
        # Simplified temperature calculation
        return 278 * math.sqrt(luminosity) / math.sqrt(distance)

    def generate_basic_atmosphere(self) -> Dict[str, float]:
        return {
            "N2": 0.78,
            "O2": 0.21,
            "Ar": 0.01
        }