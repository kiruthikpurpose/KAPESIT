import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

class Material:
    def __init__(self, name: str, density: float, thermal_conductivity: float,
                 electrical_conductivity: float, melting_point: float):
        self.name = name
        self.density = density
        self.thermal_conductivity = thermal_conductivity
        self.electrical_conductivity = electrical_conductivity
        self.melting_point = melting_point
        self.properties_history = []

    def calculate_heat_transfer(self, temperature_difference: float, area: float, thickness: float) -> float:
        return (self.thermal_conductivity * temperature_difference * area) / thickness

    def calculate_resistance(self, length: float, cross_sectional_area: float) -> float:
        return length / (self.electrical_conductivity * cross_sectional_area)

    def update_properties(self, new_properties: Dict[str, float], timestamp: datetime) -> None:
        self.properties_history.append({
            'timestamp': timestamp,
            'properties': {
                'density': self.density,
                'thermal_conductivity': self.thermal_conductivity,
                'electrical_conductivity': self.electrical_conductivity,
                'melting_point': self.melting_point
            }
        })
        
        for prop, value in new_properties.items():
            setattr(self, prop, value)

class CompositeMaterial:
    def __init__(self, name: str, components: Dict[Material, float]):
        self.name = name
        self.components = components
        self.properties = self.calculate_properties()

    def calculate_properties(self) -> Dict[str, float]:
        properties = {
            'density': 0,
            'thermal_conductivity': 0,
            'electrical_conductivity': 0,
            'melting_point': float('inf')
        }
        
        total_weight = sum(self.components.values())
        
        for material, weight in self.components.items():
            weight_fraction = weight / total_weight
            properties['density'] += material.density * weight_fraction
            properties['thermal_conductivity'] += material.thermal_conductivity * weight_fraction
            properties['electrical_conductivity'] += material.electrical_conductivity * weight_fraction
            properties['melting_point'] = min(properties['melting_point'], material.melting_point)
        
        return properties

    def add_component(self, material: Material, weight: float) -> None:
        self.components[material] = weight
        self.properties = self.calculate_properties()

    def remove_component(self, material: Material) -> bool:
        if material in self.components:
            del self.components[material]
            self.properties = self.calculate_properties()
            return True
        return False

class MaterialDatabase:
    def __init__(self):
        self.materials = {}
        self.composites = {}
        self.search_history = []

    def add_material(self, material: Material) -> None:
        self.materials[material.name] = material

    def add_composite(self, composite: CompositeMaterial) -> None:
        self.composites[composite.name] = composite

    def search_material(self, query: str) -> List[Material]:
        results = []
        query = query.lower()
        
        for material in self.materials.values():
            if query in material.name.lower():
                results.append(material)
        
        for composite in self.composites.values():
            if query in composite.name.lower():
                results.append(composite)
        
        self.search_history.append({
            'query': query,
            'timestamp': datetime.now(),
            'results_count': len(results)
        })
        
        return results

    def get_material_properties(self, name: str) -> Optional[Dict[str, float]]:
        if name in self.materials:
            return {
                'density': self.materials[name].density,
                'thermal_conductivity': self.materials[name].thermal_conductivity,
                'electrical_conductivity': self.materials[name].electrical_conductivity,
                'melting_point': self.materials[name].melting_point
            }
        elif name in self.composites:
            return self.composites[name].properties
        return None

class MaterialOptimizer:
    def __init__(self, target_properties: Dict[str, float], constraints: Dict[str, float]):
        self.target_properties = target_properties
        self.constraints = constraints
        self.optimization_history = []

    def calculate_score(self, material: Material) -> float:
        score = 0
        for prop, target in self.target_properties.items():
            current = getattr(material, prop)
            score += abs(current - target)
        return score

    def optimize_material(self, material: Material, iterations: int = 100) -> Material:
        best_material = material
        best_score = self.calculate_score(material)
        
        for _ in range(iterations):
            # Create a modified version of the material
            modified = Material(
                name=material.name,
                density=material.density + np.random.normal(0, 0.1),
                thermal_conductivity=material.thermal_conductivity + np.random.normal(0, 0.1),
                electrical_conductivity=material.electrical_conductivity + np.random.normal(0, 0.1),
                melting_point=material.melting_point + np.random.normal(0, 0.1)
            )
            
            score = self.calculate_score(modified)
            if score < best_score:
                best_material = modified
                best_score = score
        
        self.optimization_history.append({
            'initial_material': material,
            'optimized_material': best_material,
            'score_improvement': best_score,
            'timestamp': datetime.now()
        })
        
        return best_material

    def optimize_composite(self, composite: CompositeMaterial, iterations: int = 100) -> CompositeMaterial:
        best_composite = composite
        best_score = self.calculate_score(composite)
        
        for _ in range(iterations):
            # Create a modified version of the composite
            modified_components = {
                material: weight + np.random.normal(0, 0.1)
                for material, weight in composite.components.items()
            }
            
            modified_composite = CompositeMaterial(
                name=composite.name,
                components=modified_components
            )
            
            score = self.calculate_score(modified_composite)
            if score < best_score:
                best_composite = modified_composite
                best_score = score
        
        self.optimization_history.append({
            'initial_composite': composite,
            'optimized_composite': best_composite,
            'score_improvement': best_score,
            'timestamp': datetime.now()
        })
        
        return best_composite
