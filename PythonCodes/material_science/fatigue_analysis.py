from typing import Dict, List, Tuple
import math

class FatigueCycle:
    def __init__(self, max_stress: float, min_stress: float, frequency: float):
        self.max_stress = max_stress
        self.min_stress = min_stress
        self.stress_amplitude = (max_stress - min_stress) / 2
        self.mean_stress = (max_stress + min_stress) / 2
        self.frequency = frequency
        self.stress_ratio = min_stress / max_stress if max_stress != 0 else 0

class FatigueAnalyzer:
    def __init__(self):
        self.cycle_history = []
        self.damage_accumulation = 0
        
    def calculate_cycles_to_failure(self, fatigue_strength: float, 
                                  fatigue_exponent: float, 
                                  stress_amplitude: float) -> float:
        return (fatigue_strength / stress_amplitude) ** (1 / fatigue_exponent)
    
    def calculate_damage_fraction(self, cycle: FatigueCycle, 
                                material_properties: Dict[str, float]) -> float:
        Nf = self.calculate_cycles_to_failure(
            material_properties["fatigue_strength"],
            material_properties["fatigue_exponent"],
            cycle.stress_amplitude
        )
        return 1 / Nf
    
    def apply_rainflow_counting(self, stress_history: List[float]) -> List[FatigueCycle]:
        cycles = []
        stack = []
        
        for stress in stress_history:
            while len(stack) >= 3:
                range1 = abs(stack[-2] - stack[-3])
                range2 = abs(stack[-1] - stack[-2])
                
                if range1 >= range2:
                    cycle = FatigueCycle(max(stack[-2], stack[-3]), 
                                       min(stack[-2], stack[-3]), 1.0)
                    cycles.append(cycle)
                    stack.pop(-2)
                else:
                    break
                    
            stack.append(stress)
            
        return cycles