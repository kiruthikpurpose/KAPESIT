from typing import Dict, List, Tuple
import math

class OrbitalParameters:
    def __init__(self, semi_major_axis: float, eccentricity: float, inclination: float):
        self.semi_major_axis = semi_major_axis
        self.eccentricity = eccentricity
        self.inclination = inclination
        self.period = self.calculate_orbital_period()
        
    def calculate_orbital_period(self) -> float:
        G = 6.67430e-11
        M = 1.989e30
        return 2 * math.pi * math.sqrt(self.semi_major_axis**3 / (G * M))
    
    def calculate_velocity(self, radius: float) -> float:
        G = 6.67430e-11
        M = 1.989e30
        return math.sqrt(G * M * (2/radius - 1/self.semi_major_axis))

class TrajectoryCalculator:
    def __init__(self):
        self.trajectories = []
        
    def calculate_hohmann_transfer(self, r1: float, r2: float) -> Dict[str, float]:
        G = 6.67430e-11
        M = 1.989e30
        
        transfer_a = (r1 + r2) / 2
        v1 = math.sqrt(G * M / r1)
        v2 = math.sqrt(G * M / r2)
        
        delta_v1 = math.sqrt(G * M * (2/r1 - 2/(r1 + r2))) - v1
        delta_v2 = v2 - math.sqrt(G * M * (2/r2 - 2/(r1 + r2)))
        
        transfer_time = math.pi * math.sqrt(transfer_a**3 / (G * M))
        
        return {
            "delta_v1": delta_v1,
            "delta_v2": delta_v2,
            "total_delta_v": abs(delta_v1) + abs(delta_v2),
            "transfer_time": transfer_time
        }