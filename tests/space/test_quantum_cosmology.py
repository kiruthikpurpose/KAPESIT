import numpy as np
import pytest
from kapesit.space.quantum_cosmology import QuantumCosmology

def test_quantum_cosmology():
    cosmology = QuantumCosmology(num_qubits=4)
    
    scale_factor = 1.0
    result = cosmology.simulate_universe(scale_factor)
    assert "energy" in result
    assert "state" in result
    assert "scale_factor" in result
    assert isinstance(result["energy"], float)
    
    hubble = cosmology.calculate_hubble_parameter(scale_factor)
    assert isinstance(hubble, float)
    assert hubble >= 0
    
    inflation = cosmology.simulate_inflation(scale_factor, num_steps=10)
    assert len(inflation) == 10
    assert all("energy" in r for r in inflation)
    
    entropy = cosmology.calculate_entropy(scale_factor)
    assert isinstance(entropy, float)
    assert entropy >= 0
    
    fluctuations = cosmology.simulate_quantum_fluctuation(scale_factor, num_steps=10)
    assert len(fluctuations) == 10
    assert all("energy" in f for f in fluctuations)
    
    correlation = cosmology.calculate_correlation(scale_factor, distance=1)
    assert isinstance(correlation, float)
    assert 0 <= correlation <= 1
    
    transition = cosmology.simulate_phase_transition(scale_factor, 2 * scale_factor)
    assert "probability" in transition
    assert 0 <= transition["probability"] <= 1

def test_error_handling():
    cosmology = QuantumCosmology(num_qubits=4)
    
    with pytest.raises(Exception):
        cosmology.simulate_universe(-1.0)
    
    with pytest.raises(Exception):
        cosmology.calculate_hubble_parameter(-1.0)
    
    with pytest.raises(Exception):
        cosmology.simulate_inflation(-1.0)
    
    with pytest.raises(Exception):
        cosmology.calculate_entropy(-1.0)
    
    with pytest.raises(Exception):
        cosmology.simulate_quantum_fluctuation(-1.0)
    
    with pytest.raises(Exception):
        cosmology.calculate_correlation(-1.0, distance=1)
    
    with pytest.raises(Exception):
        cosmology.simulate_phase_transition(-1.0, 2.0)

def test_integration():
    cosmology = QuantumCosmology(num_qubits=4)
    
    scale_factor = 1.0
    result = cosmology.simulate_universe(scale_factor)
    hubble = cosmology.calculate_hubble_parameter(scale_factor)
    entropy = cosmology.calculate_entropy(scale_factor)
    
    assert isinstance(result["energy"], float)
    assert isinstance(hubble, float)
    assert isinstance(entropy, float)
    
    inflation = cosmology.simulate_inflation(scale_factor)
    fluctuations = cosmology.simulate_quantum_fluctuation(inflation[-1]["scale_factor"])
    
    assert len(fluctuations) == 100
    assert all("energy" in f for f in fluctuations)
    
    transition = cosmology.simulate_phase_transition(scale_factor, inflation[-1]["scale_factor"])
    assert "probability" in transition
    assert 0 <= transition["probability"] <= 1 