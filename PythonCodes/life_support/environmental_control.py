from typing import Dict, List, Tuple
import math

class AtmosphereProcessor:
    def __init__(self, volume: float, initial_composition: Dict[str, float]):
        self.volume = volume
        self.composition = initial_composition
        self.temperature = 293.15
        self.pressure = 101325
        
    def calculate_partial_pressures(self) -> Dict[str, float]:
        return {gas: concentration * self.pressure 
                for gas, concentration in self.composition.items()}
    
    def simulate_gas_exchange(self, consumption_rates: Dict[str, float], 
                            time_step: float) -> Dict[str, float]:
        total_moles = self.pressure * self.volume / (8.314 * self.temperature)
        
        for gas, rate in consumption_rates.items():
            if gas in self.composition:
                delta_moles = rate * time_step
                current_moles = total_moles * self.composition[gas]
                new_moles = max(0, current_moles - delta_moles)
                self.composition[gas] = new_moles / total_moles
                
        return self.composition

class WaterRecyclingSystem:
    def __init__(self, capacity: float, efficiency: float):
        self.capacity = capacity
        self.efficiency = efficiency
        self.contamination_level = 0
        self.filter_status = 1.0
        
    def process_water(self, volume: float, contamination: float) -> Dict[str, float]:
        processed_volume = min(volume, self.capacity)
        effective_efficiency = self.efficiency * self.filter_status
        
        cleaned_water = processed_volume * effective_efficiency
        contamination_removed = contamination * effective_efficiency
        
        self.contamination_level += contamination * (1 - effective_efficiency)
        self.filter_status *= 0.99
        
        return {
            "cleaned_volume": cleaned_water,
            "contamination_removed": contamination_removed,
            "filter_status": self.filter_status,
            "system_efficiency": effective_efficiency
        }
    
    def calculate_maintenance_needs(self) -> Dict[str, float]:
        filter_lifetime = -math.log(self.filter_status) / 0.01
        maintenance_urgency = 1 - self.filter_status
        
        return {
            "filter_lifetime_hours": filter_lifetime,
            "maintenance_urgency": maintenance_urgency,
            "contamination_level": self.contamination_level
        }