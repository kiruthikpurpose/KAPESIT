import numpy as np
import pytest
from kapesit.quantum.chemistry import (
    QuantumChemistry,
    QuantumDynamics,
    QuantumReaction
)

def test_quantum_chemistry():
    # Test with H2 molecule
    geometry = [("H", [0, 0, 0]), ("H", [0, 0, 0.74])]
    qc = QuantumChemistry(geometry)
    
    # Test ground state calculation
    ground_state = qc.solve_ground_state()
    assert "energy" in ground_state
    assert "optimal_point" in ground_state
    assert "optimal_circuit" in ground_state
    
    # Test excited states calculation
    excited_states = qc.solve_excited_states(num_states=2)
    assert "ground_state_energy" in excited_states
    assert "excited_state_energies" in excited_states
    assert "excited_state_circuits" in excited_states
    
    # Test properties calculation
    properties = qc.calculate_properties()
    assert "dipole_moment" in properties
    assert "mulliken_charges" in properties
    assert "molecular_orbitals" in properties
    
    # Test force constants calculation
    force_constants = qc.calculate_force_constants()
    assert "harmonic" in force_constants
    assert "anharmonic" in force_constants
    
    # Test spectrum calculation
    spectrum = qc.calculate_spectrum()
    assert "vibrational" in spectrum
    assert "electronic" in spectrum

def test_quantum_dynamics():
    geometry = [("H", [0, 0, 0]), ("H", [0, 0, 0.74])]
    qc = QuantumChemistry(geometry)
    dynamics = QuantumDynamics(qc)
    
    # Set initial state
    initial_state = np.zeros(2**qc.num_orbitals)
    initial_state[0] = 1.0
    dynamics.set_initial_state(initial_state)
    
    # Test propagation
    time_steps = [0, 0.1, 0.2]
    propagation = dynamics.propagate(time_steps)
    assert "times" in propagation
    assert "states" in propagation
    assert "energies" in propagation
    assert len(propagation["times"]) == len(time_steps)
    
    # Test observable calculation
    observable = np.eye(2**qc.num_orbitals)
    measurements = dynamics.calculate_observables(observable, time_steps)
    assert "times" in measurements
    assert "measurements" in measurements
    assert len(measurements["times"]) == len(time_steps)
    
    with pytest.raises(ValueError):
        dynamics = QuantumDynamics(qc)
        dynamics.propagate(time_steps)

def test_quantum_reaction():
    # Test H2 + H2 -> H2 + H2 reaction
    reactant_geometry = [
        ("H", [0, 0, 0]),
        ("H", [0, 0, 0.74]),
        ("H", [2, 0, 0]),
        ("H", [2, 0, 0.74])
    ]
    product_geometry = [
        ("H", [0, 0, 0]),
        ("H", [0, 0, 0.74]),
        ("H", [2, 0, 0]),
        ("H", [2, 0, 0.74])
    ]
    
    reaction = QuantumReaction(reactant_geometry, product_geometry)
    
    # Test reaction energy calculation
    energy = reaction.calculate_reaction_energy()
    assert "reactant_energy" in energy
    assert "product_energy" in energy
    assert "reaction_energy" in energy
    
    # Test reaction path calculation
    path = reaction.calculate_reaction_path(num_points=5)
    assert "path_coordinates" in path
    assert "path_energies" in path
    assert len(path["path_coordinates"]) == 5
    assert len(path["path_energies"]) == 5
    
    # Test transition state calculation
    ts = reaction.calculate_transition_state()
    assert "transition_state_coordinates" in ts
    assert "transition_state_energy" in ts
    assert "activation_energy" in ts

def test_integration():
    # Test integration between different components
    geometry = [("H", [0, 0, 0]), ("H", [0, 0, 0.74])]
    qc = QuantumChemistry(geometry)
    dynamics = QuantumDynamics(qc)
    
    # Calculate ground state
    ground_state = qc.solve_ground_state()
    
    # Set initial state for dynamics
    initial_state = np.zeros(2**qc.num_orbitals)
    initial_state[0] = 1.0
    dynamics.set_initial_state(initial_state)
    
    # Propagate dynamics
    time_steps = [0, 0.1]
    propagation = dynamics.propagate(time_steps)
    
    # Calculate observables
    observable = np.eye(2**qc.num_orbitals)
    measurements = dynamics.calculate_observables(observable, time_steps)
    
    assert len(propagation["times"]) == len(time_steps)
    assert len(measurements["times"]) == len(time_steps) 