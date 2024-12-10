from typing import Dict, List, Tuple
import math

class ThermalProperties:
    def __init__(self, conductivity: float, specific_heat: float, density: float):
        self.conductivity = conductivity
        self.specific_heat = specific_heat
        self.density = density
        self.thermal_diffusivity = conductivity / (density * specific_heat)

class ThermalAnalyzer:
    def __init__(self):
        self.temperature_history = []
        
    def calculate_heat_flux(self, thermal_props: ThermalProperties, 
                          temp_gradient: float, thickness: float) -> float:
        return -thermal_props.conductivity * temp_gradient / thickness
    
    def simulate_thermal_cycle(self, material: ThermalProperties, 
                             max_temp: float, min_temp: float, 
                             cycle_time: float) -> List[Tuple[float, float]]:
        results = []
        time_step = cycle_time / 100
        
        for t in range(101):
            current_time = t * time_step
            temperature = (max_temp + min_temp) / 2 + \
                         (max_temp - min_temp) / 2 * \
                         math.sin(2 * math.pi * current_time / cycle_time)
            results.append((current_time, temperature))
            
        return results
    
    def calculate_thermal_stress_field(self, material: ThermalProperties, 
                                     temperature_distribution: List[float], 
                                     young_modulus: float, 
                                     thermal_expansion: float) -> List[float]:
        stress_field = []
        reference_temp = temperature_distribution[0]
        
        for temp in temperature_distribution:
            thermal_strain = thermal_expansion * (temp - reference_temp)
            thermal_stress = young_modulus * thermal_strain
            stress_field.append(thermal_stress)
            
        return stress_field