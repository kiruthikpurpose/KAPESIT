import numpy as np
import pytest
from kapesit.quantum.simulation import (
    HamiltonianSimulator,
    QuantumDynamics,
    QuantumCircuitSimulator,
    QuantumErrorMitigation
)
from qiskit import QuantumCircuit

def test_hamiltonian_simulator():
    # Test with a simple 2x2 Hamiltonian
    hamiltonian = np.array([[1, 0], [0, -1]])
    simulator = HamiltonianSimulator(hamiltonian)
    
    # Test diagonalization
    assert np.allclose(simulator.eigenvalues, np.array([-1, 1]))
    
    # Test time evolution
    initial_state = np.array([1, 0])
    evolved_state = simulator.time_evolution(initial_state, np.pi/2)
    assert np.allclose(np.abs(evolved_state), np.array([0, 1]), atol=1e-6)
    
    # Test expectation value
    observable = np.array([[0, 1], [1, 0]])
    exp_value = simulator.expectation_value(initial_state, observable)
    assert np.isclose(exp_value, 0)
    
    # Test ground state
    ground_state, ground_energy = simulator.ground_state()
    assert np.isclose(ground_energy, -1)
    assert np.allclose(ground_state, np.array([0, 1]))

def test_quantum_dynamics():
    # Test with a simple 2x2 Hamiltonian
    hamiltonian = np.array([[1, 0], [0, -1]])
    initial_state = np.array([1, 0])
    dynamics = QuantumDynamics(hamiltonian, initial_state)
    
    # Test evolution
    times = [0, np.pi/2, np.pi]
    evolution = dynamics.evolve(times)
    
    assert len(evolution["times"]) == len(times)
    assert len(evolution["states"]) == len(times)
    assert len(evolution["energies"]) == len(times)
    
    # Test observable measurement
    observable = np.array([[0, 1], [1, 0]])
    measurements = dynamics.measure_observable(observable, times)
    
    assert len(measurements["times"]) == len(times)
    assert len(measurements["measurements"]) == len(times)

def test_quantum_circuit_simulator():
    # Test with a simple 2-qubit circuit
    simulator = QuantumCircuitSimulator(2)
    
    # Add some gates
    simulator.add_gate("H", 0)
    simulator.add_gate("CNOT", 0, [1])
    
    # Test simulation
    result = simulator.simulate()
    assert "unitary" in result
    assert "final_state" in result
    assert result["unitary"].shape == (4, 4)
    assert result["final_state"].shape == (4,)
    
    # Test measurement
    counts = simulator.measure(num_shots=1000)
    assert isinstance(counts, dict)
    assert sum(counts.values()) == 1000

def test_quantum_error_mitigation():
    # Create a simple circuit
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    
    # Test error mitigation
    mitigator = QuantumErrorMitigation(circuit)
    noise_factors = [1.0, 2.0, 3.0]
    results = mitigator.apply_zero_noise_extrapolation(noise_factors)
    
    assert "noisy_results" in results
    assert "zero_noise_result" in results
    assert len(results["noisy_results"]) == len(noise_factors)

def test_integration():
    # Test integration between different components
    hamiltonian = np.array([[1, 0], [0, -1]])
    simulator = HamiltonianSimulator(hamiltonian)
    initial_state = np.array([1, 0])
    dynamics = QuantumDynamics(hamiltonian, initial_state)
    
    # Create a circuit based on the Hamiltonian evolution
    circuit_simulator = QuantumCircuitSimulator(1)
    circuit_simulator.add_gate("RX", 0, [np.pi/2])
    
    # Apply error mitigation
    mitigator = QuantumErrorMitigation(circuit_simulator.circuit)
    results = mitigator.apply_zero_noise_extrapolation([1.0, 2.0])
    
    assert "noisy_results" in results
    assert "zero_noise_result" in results 