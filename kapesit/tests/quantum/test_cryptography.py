import numpy as np
import pytest
from kapesit.quantum.cryptography import BB84Protocol, E91Protocol, QuantumKeyDistribution

def test_bb84_protocol():
    num_qubits = 100
    protocol = BB84Protocol(num_qubits)
    
    # Test initialization
    assert len(protocol.alice_basis) == num_qubits
    assert len(protocol.bob_basis) == num_qubits
    assert len(protocol.key) == num_qubits
    
    # Test circuit preparation
    circuit = protocol.alice_prepare()
    assert circuit.num_qubits == num_qubits
    
    # Test measurement
    circuit = protocol.bob_measure(circuit)
    assert circuit.num_qubits == num_qubits
    
    # Test key sifting
    alice_key, bob_key = protocol.sift_key()
    assert len(alice_key) == len(bob_key)
    assert len(alice_key) <= num_qubits
    
    # Test error estimation
    error_rate = protocol.estimate_error(alice_key, bob_key, min(10, len(alice_key)))
    assert 0 <= error_rate <= 1

def test_e91_protocol():
    num_pairs = 100
    protocol = E91Protocol(num_pairs)
    
    # Test initialization
    assert len(protocol.alice_basis) == num_pairs
    assert len(protocol.bob_basis) == num_pairs
    assert len(protocol.entangled_pairs) == num_pairs
    
    # Test measurements
    alice_measurements = protocol.alice_measure()
    bob_measurements = protocol.bob_measure()
    assert len(alice_measurements) == num_pairs
    assert len(bob_measurements) == num_pairs
    
    # Test correlation calculation
    correlation = protocol.calculate_correlation(alice_measurements, bob_measurements)
    assert 0 <= correlation <= 1
    
    # Test Bell inequality
    bell_violation = protocol.check_bell_inequality(alice_measurements, bob_measurements)
    assert isinstance(bell_violation, bool)

def test_quantum_key_distribution():
    # Test BB84
    qkd_bb84 = QuantumKeyDistribution(protocol='BB84', num_qubits=100)
    alice_key, bob_key = qkd_bb84.generate_key()
    assert len(alice_key) == len(bob_key)
    security = qkd_bb84.verify_security(alice_key, bob_key)
    assert isinstance(security, bool)
    
    # Test E91
    qkd_e91 = QuantumKeyDistribution(protocol='E91', num_qubits=100)
    alice_key, bob_key = qkd_e91.generate_key()
    assert len(alice_key) == len(bob_key)
    security = qkd_e91.verify_security(alice_key, bob_key)
    assert isinstance(security, bool)
    
    # Test error handling
    with pytest.raises(ValueError):
        QuantumKeyDistribution(protocol='invalid')

def test_integration():
    # Test integration between BB84 and E91
    qkd_bb84 = QuantumKeyDistribution(protocol='BB84', num_qubits=100)
    qkd_e91 = QuantumKeyDistribution(protocol='E91', num_qubits=100)
    
    # Generate keys
    bb84_alice, bb84_bob = qkd_bb84.generate_key()
    e91_alice, e91_bob = qkd_e91.generate_key()
    
    # Verify security
    bb84_security = qkd_bb84.verify_security(bb84_alice, bb84_bob)
    e91_security = qkd_e91.verify_security(e91_alice, e91_bob)
    
    assert isinstance(bb84_security, bool)
    assert isinstance(e91_security, bool) 