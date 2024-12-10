from typing import Dict, List, Tuple
import math

class CelestialObject:
    def __init__(self, name: str, ra: float, dec: float, magnitude: float):
        self.name = name
        self.ra = ra
        self.dec = dec
        self.magnitude = magnitude
        
    def calculate_position(self, time: float) -> Tuple[float, float, float]:
        x = math.cos(self.dec) * math.cos(self.ra)
        y = math.cos(self.dec) * math.sin(self.ra)
        z = math.sin(self.dec)
        return (x, y, z)

class NavigationSystem:
    def __init__(self):
        self.reference_stars = []
        self.position_history = []
        
    def triangulate_position(self, star_measurements: List[Tuple[str, float, float]]) -> Dict[str, float]:
        if len(star_measurements) < 3:
            return {"error": "Insufficient star measurements"}
            
        position = {"x": 0.0, "y": 0.0, "z": 0.0}
        weights = []
        
        for star, azimuth, elevation in star_measurements:
            r = math.cos(elevation)
            x = r * math.cos(azimuth)
            y = r * math.sin(azimuth)
            z = math.sin(elevation)
            
            weight = 1.0 / (1.0 + abs(z))
            weights.append(weight)
            
            position["x"] += x * weight
            position["y"] += y * weight
            position["z"] += z * weight
            
        total_weight = sum(weights)
        position["x"] /= total_weight
        position["y"] /= total_weight
        position["z"] /= total_weight
        
        return position
    
    def calculate_trajectory_correction(self, current_position: Dict[str, float],
                                     target_position: Dict[str, float],
                                     velocity: Dict[str, float]) -> Dict[str, float]:
        delta_x = target_position["x"] - current_position["x"]
        delta_y = target_position["y"] - current_position["y"]
        delta_z = target_position["z"] - current_position["z"]
        
        distance = math.sqrt(delta_x**2 + delta_y**2 + delta_z**2)
        
        if distance < 1e-6:
            return {"thrust_x": 0, "thrust_y": 0, "thrust_z": 0}
            
        desired_velocity = {
            "x": delta_x / distance,
            "y": delta_y / distance,
            "z": delta_z / distance
        }
        
        return {
            "thrust_x": desired_velocity["x"] - velocity["x"],
            "thrust_y": desired_velocity["y"] - velocity["y"],
            "thrust_z": desired_velocity["z"] - velocity["z"]
        }