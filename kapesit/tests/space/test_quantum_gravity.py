import numpy as np
import pytest
from kapesit.space.quantum_gravity import QuantumGravity

def test_quantum_gravity():
    gravity = QuantumGravity(num_qubits=4)
    
    metric = np.eye(4)
    result = gravity.simulate_gravity(metric)
    assert "energy" in result
    assert "state" in result
    assert "metric" in result
    assert isinstance(result["energy"], float)
    
    curvature = gravity.calculate_curvature(metric)
    assert isinstance(curvature, float)
    assert curvature >= 0
    
    black_hole = gravity.simulate_black_hole(mass=1.0, charge=0.5)
    assert "mass" in black_hole
    assert "charge" in black_hole
    assert "curvature" in black_hole
    assert black_hole["mass"] == 1.0
    assert black_hole["charge"] == 0.5
    
    fluctuations = gravity.simulate_quantum_fluctuation(metric, num_steps=10)
    assert len(fluctuations) == 10
    assert all("energy" in f for f in fluctuations)
    
    entropy = gravity.calculate_entropy(metric)
    assert isinstance(entropy, float)
    assert entropy >= 0
    
    initial_metric = np.eye(4)
    final_metric = 2 * np.eye(4)
    tunneling = gravity.simulate_quantum_tunneling(initial_metric, final_metric)
    assert "probability" in tunneling
    assert 0 <= tunneling["probability"] <= 1

def test_error_handling():
    gravity = QuantumGravity(num_qubits=4)
    
    with pytest.raises(Exception):
        gravity.simulate_gravity(np.eye(3))
    
    with pytest.raises(Exception):
        gravity.calculate_curvature(np.eye(3))
    
    with pytest.raises(Exception):
        gravity.simulate_black_hole(mass=-1.0, charge=0.5)
    
    with pytest.raises(Exception):
        gravity.simulate_quantum_fluctuation(np.eye(3))
    
    with pytest.raises(Exception):
        gravity.calculate_entropy(np.eye(3))
    
    with pytest.raises(Exception):
        gravity.simulate_quantum_tunneling(np.eye(3), np.eye(4))

def test_integration():
    gravity = QuantumGravity(num_qubits=4)
    
    metric = np.eye(4)
    result = gravity.simulate_gravity(metric)
    curvature = gravity.calculate_curvature(metric)
    entropy = gravity.calculate_entropy(metric)
    
    assert isinstance(result["energy"], float)
    assert isinstance(curvature, float)
    assert isinstance(entropy, float)
    
    black_hole = gravity.simulate_black_hole(mass=1.0, charge=0.5)
    fluctuations = gravity.simulate_quantum_fluctuation(black_hole["metric"])
    
    assert len(fluctuations) == 100
    assert all("energy" in f for f in fluctuations)
    
    tunneling = gravity.simulate_quantum_tunneling(metric, black_hole["metric"])
    assert "probability" in tunneling
    assert 0 <= tunneling["probability"] <= 1 