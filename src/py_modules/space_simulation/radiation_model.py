from typing import Dict, List
import math

class RadiationField:
    def __init__(self, intensity: float, spectrum: Dict[str, float]):
        self.intensity = intensity
        self.spectrum = spectrum
        self.total_dose = 0
        
    def calculate_dose_rate(self, shielding_thickness: float) -> float:
        attenuation = math.exp(-shielding_thickness * 0.693)
        return self.intensity * attenuation
    
    def accumulate_dose(self, exposure_time: float, shielding_thickness: float) -> float:
        dose_rate = self.calculate_dose_rate(shielding_thickness)
        self.total_dose += dose_rate * exposure_time
        return self.total_dose

class ShieldingCalculator:
    def __init__(self):
        self.material_coefficients = {
            "aluminum": 2.7,
            "lead": 11.34,
            "water": 1.0,
            "polyethylene": 0.94
        }
    
    def calculate_required_thickness(self, material: str, target_dose: float, 
                                  radiation_field: RadiationField) -> float:
        if material not in self.material_coefficients:
            return float('inf')
            
        coefficient = self.material_coefficients[material]
        return -math.log(target_dose / radiation_field.intensity) / (coefficient * 0.693)
    
    def optimize_multilayer_shield(self, materials: List[str], 
                                target_dose: float, 
                                radiation_field: RadiationField) -> Dict[str, float]:
        thicknesses = {}
        remaining_dose = target_dose
        
        for material in materials:
            thickness = self.calculate_required_thickness(material, remaining_dose, 
                                                      radiation_field)
            thicknesses[material] = thickness
            remaining_dose *= math.exp(-thickness * 
                                    self.material_coefficients[material] * 0.693)
            
        return thicknesses