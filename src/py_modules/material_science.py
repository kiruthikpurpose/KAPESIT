from typing import Dict, List
import math

class Material:
    def __init__(self, name: str, properties: Dict[str, float]):
        self.name = name
        self.properties = properties
        self.stress_history = []

    def calculate_thermal_stress(self, temperature_change: float) -> float:
        """Calculate thermal stress under temperature change"""
        if "thermal_expansion" in self.properties and "young_modulus" in self.properties:
            thermal_expansion = self.properties["thermal_expansion"]
            young_modulus = self.properties["young_modulus"]
            return thermal_expansion * young_modulus * temperature_change
        return 0.0

    def estimate_fatigue_life(self, stress_amplitude: float) -> float:
        """Estimate material fatigue life using basic S-N curve approximation"""
        if "fatigue_strength" in self.properties and "fatigue_exponent" in self.properties:
            strength = self.properties["fatigue_strength"]
            exponent = self.properties["fatigue_exponent"]
            return strength * math.pow(stress_amplitude, -1/exponent)
        return 0.0

class MaterialSimulator:
    def __init__(self):
        self.materials_database = {}

    def create_material(self, name: str, properties: Dict[str, float]) -> Material:
        material = Material(name, properties)
        self.materials_database[name] = material
        return material

    def simulate_extreme_conditions(self, 
                                  material: Material, 
                                  temperature: float, 
                                  pressure: float) -> Dict[str, float]:
        """Simulate material behavior under extreme conditions"""
        results = {}
        
        # Thermal effects
        thermal_stress = material.calculate_thermal_stress(temperature - 293.15)  # from room temp
        results["thermal_stress"] = thermal_stress
        
        # Pressure effects
        if "bulk_modulus" in material.properties:
            volume_strain = pressure / material.properties["bulk_modulus"]
            results["volume_strain"] = volume_strain
        
        # Strength adjustment
        if "yield_strength" in material.properties:
            # Simple linear approximation of temperature effect on strength
            temp_factor = max(0.1, 1 - (temperature - 293.15) / 1000)
            adjusted_strength = material.properties["yield_strength"] * temp_factor
            results["adjusted_strength"] = adjusted_strength
        
        return results