import numpy as np
import pytest
from kapesit.materials.quantum_materials import QuantumMaterial

def test_quantum_material():
    # Test with H2 molecule
    geometry = [("H", [0, 0, 0]), ("H", [0, 0, 0.74])]
    material = QuantumMaterial(geometry)
    
    # Test initialization
    assert material.num_particles == 2
    assert material.num_orbitals > 0
    
    # Test band structure calculation
    k_points = [[0, 0, 0], [0.5, 0.5, 0.5]]
    band_structure = material.calculate_band_structure(k_points)
    assert len(band_structure) == len(k_points)
    assert all(isinstance(energy, float) for energy in band_structure.values())
    
    # Test density of states calculation
    energy_range = [-10, 10]
    dos = material.calculate_density_of_states(energy_range)
    assert "energies" in dos
    assert "dos" in dos
    assert len(dos["energies"]) == 100
    assert len(dos["dos"]) == 100
    assert all(d >= 0 for d in dos["dos"])
    
    # Test phonon bands calculation
    q_points = [[0, 0, 0], [0.5, 0.5, 0.5]]
    phonon_bands = material.calculate_phonon_bands(q_points)
    assert len(phonon_bands) == len(q_points)
    assert all(isinstance(energy, float) for energy in phonon_bands.values())
    
    # Test thermal properties calculation
    temperature_range = [0, 300]
    thermal_properties = material.calculate_thermal_properties(temperature_range)
    assert "temperatures" in thermal_properties
    assert "heat_capacity" in thermal_properties
    assert "entropy" in thermal_properties
    assert "free_energy" in thermal_properties
    assert len(thermal_properties["temperatures"]) == 100
    assert len(thermal_properties["heat_capacity"]) == 100
    assert len(thermal_properties["entropy"]) == 100
    assert len(thermal_properties["free_energy"]) == 100
    assert all(cv >= 0 for cv in thermal_properties["heat_capacity"])
    assert all(s >= 0 for s in thermal_properties["entropy"])

def test_error_handling():
    # Test with invalid geometry
    with pytest.raises(Exception):
        QuantumMaterial([("H", [0, 0])])
    
    # Test with invalid basis
    with pytest.raises(Exception):
        QuantumMaterial([("H", [0, 0, 0]), ("H", [0, 0, 0.74])], basis="invalid")
    
    # Test with invalid k-points
    material = QuantumMaterial([("H", [0, 0, 0]), ("H", [0, 0, 0.74])])
    with pytest.raises(Exception):
        material.calculate_band_structure([[0, 0]])
    
    # Test with invalid energy range
    with pytest.raises(Exception):
        material.calculate_density_of_states([10, 0])
    
    # Test with invalid temperature range
    with pytest.raises(Exception):
        material.calculate_thermal_properties([300, 0])

def test_integration():
    # Test integration between different calculations
    geometry = [("H", [0, 0, 0]), ("H", [0, 0, 0.74])]
    material = QuantumMaterial(geometry)
    
    # Calculate band structure
    k_points = [[0, 0, 0], [0.5, 0.5, 0.5]]
    band_structure = material.calculate_band_structure(k_points)
    
    # Calculate density of states
    energy_range = [min(band_structure.values()), max(band_structure.values())]
    dos = material.calculate_density_of_states(energy_range)
    
    # Calculate phonon bands
    q_points = [[0, 0, 0], [0.5, 0.5, 0.5]]
    phonon_bands = material.calculate_phonon_bands(q_points)
    
    # Calculate thermal properties
    temperature_range = [0, 300]
    thermal_properties = material.calculate_thermal_properties(temperature_range)
    
    # Verify results
    assert len(band_structure) == len(k_points)
    assert len(dos["energies"]) == 100
    assert len(phonon_bands) == len(q_points)
    assert len(thermal_properties["temperatures"]) == 100 