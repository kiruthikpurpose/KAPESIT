import numpy as np
import pytest
from kapesit.space.quantum_field import QuantumField

def test_quantum_field():
    field = QuantumField(num_qubits=4)
    
    field_config = np.eye(4)
    result = field.simulate_field(field_config)
    assert "energy" in result
    assert "state" in result
    assert "field" in result
    assert isinstance(result["energy"], float)
    
    vacuum_energy = field.calculate_vacuum_energy(field_config)
    assert isinstance(vacuum_energy, float)
    
    particles = field.simulate_particle_creation(field_config, num_particles=2)
    assert "field" in particles
    assert "particles" in particles
    assert "energy" in particles
    assert len(particles["particles"]) == 2
    assert all("position" in p for p in particles["particles"])
    assert all("momentum" in p for p in particles["particles"])
    assert all("energy" in p for p in particles["particles"])
    
    fluctuations = field.simulate_field_fluctuation(field_config, num_steps=10)
    assert len(fluctuations) == 10
    assert all("energy" in f for f in fluctuations)
    
    correlation = field.calculate_correlation(field_config, distance=1)
    assert isinstance(correlation, float)
    assert 0 <= correlation <= 1
    
    initial_config = np.eye(4)
    final_config = 2 * np.eye(4)
    transition = field.simulate_phase_transition(initial_config, final_config)
    assert "probability" in transition
    assert 0 <= transition["probability"] <= 1

def test_error_handling():
    field = QuantumField(num_qubits=4)
    
    with pytest.raises(Exception):
        field.simulate_field(np.eye(3))
    
    with pytest.raises(Exception):
        field.calculate_vacuum_energy(np.eye(3))
    
    with pytest.raises(Exception):
        field.simulate_particle_creation(np.eye(3), num_particles=2)
    
    with pytest.raises(Exception):
        field.simulate_field_fluctuation(np.eye(3))
    
    with pytest.raises(Exception):
        field.calculate_correlation(np.eye(3), distance=1)
    
    with pytest.raises(Exception):
        field.simulate_phase_transition(np.eye(3), np.eye(4))

def test_integration():
    field = QuantumField(num_qubits=4)
    
    field_config = np.eye(4)
    result = field.simulate_field(field_config)
    vacuum_energy = field.calculate_vacuum_energy(field_config)
    correlation = field.calculate_correlation(field_config, distance=1)
    
    assert isinstance(result["energy"], float)
    assert isinstance(vacuum_energy, float)
    assert isinstance(correlation, float)
    
    particles = field.simulate_particle_creation(field_config, num_particles=2)
    fluctuations = field.simulate_field_fluctuation(particles["field"])
    
    assert len(fluctuations) == 100
    assert all("energy" in f for f in fluctuations)
    
    transition = field.simulate_phase_transition(field_config, particles["field"])
    assert "probability" in transition
    assert 0 <= transition["probability"] <= 1 